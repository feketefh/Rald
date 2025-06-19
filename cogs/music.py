import discord
from discord.ext import commands
from discord import option
from discord.ui import View, Button

import wavelink
import asyncio
import difflib
import os
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

class Music(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.connect_nodes())
        self.players = {}
        self.guild_locks = {}


    async def connect_nodes(self):
        """Connect to Lavalink nodes."""
        await self.bot.wait_until_ready()

        if any(node.identifier == "Node1" for node in wavelink.Pool.nodes.values()):
            print("⚠️ Lavalink Node 'Node1' is already connected.")
            return

        try:
            nodes = [
                wavelink.Node(
                    identifier="Node1",
                    uri=os.getenv("LAVALINK_URI"),
                    password=os.getenv("LAVALINK_PASSWORD")
                )
            ]
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            print("✅ Connected to Lavalink.")
        except Exception as e:
            print(f"❌ Lavalink connection failed: {e}")

    music = discord.SlashCommandGroup("music", "Music commands")

    def get_player(self, guild: discord.Guild):
        return wavelink.Pool.get_node().get_player(guild.id)
    

    async def _search_and_select_track(self, ctx: discord.ApplicationContext, query: str) -> wavelink.Playable | None:
        SEARCH_TIMEOUT = 30
        TRACK_LIMIT = 10
        SIMILARITY_THRESHOLD = 0.85

        def normalize_title(title: str) -> str:
            title = title.lower()
            title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
            title = re.sub(r"(lyrics|lyric video|official|audio|video|feat\.?|ft\.?)", "", title)
            title = re.sub(r"[^a-z0-9\s]", "", title)
            title = re.sub(r"\s+", " ", title).strip()
            return title

        yt_tracks = await wavelink.Pool.fetch_tracks(f"ytsearch:{query}")
        sc_tracks = await wavelink.Pool.fetch_tracks(f"scsearch:{query}")
        all_tracks = (yt_tracks or []) + (sc_tracks or [])

        filtered_tracks = []
        seen_titles = []

        for track in all_tracks:
            norm_title = normalize_title(track.title)
            duration = int(track.length)

            is_duplicate = False
            for seen_title, seen_duration in seen_titles:
                similarity = difflib.SequenceMatcher(None, norm_title, seen_title).ratio()
                if similarity >= SIMILARITY_THRESHOLD and abs(seen_duration - duration) < 2000:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_titles.append((norm_title, duration))
                filtered_tracks.append(track)

            if len(filtered_tracks) >= TRACK_LIMIT:
                break

        if not filtered_tracks:
            await ctx.respond("❌ No distinct results found.", ephemeral=True)
            return None

        track_list = "\n".join(
            f"`{i+1}.` **[{t.title}]({t.uri})** - {t.author}" for i, t in enumerate(filtered_tracks)
        )
        embed = discord.Embed(
            title="🔍 **Top Search Results**",
            description=track_list,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="📌 Reply with a number to select a song.")

        await ctx.respond(embed=embed)

        def check(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit()

        try:
            user_msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=SEARCH_TIMEOUT)
            choice = int(user_msg.content)

            if not 1 <= choice <= len(filtered_tracks):
                await ctx.followup.send("❌ Invalid selection! Please choose a number from the list.")
                return None

            return filtered_tracks[choice - 1]

        except asyncio.TimeoutError:
            await ctx.followup.send("⏳ **Time's up!** No song was chosen.")
            return None


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        """Leaves the voice channel if everyone leaves."""
        if not member.guild.voice_client:
            return

        vc: discord.VoiceClient = member.guild.voice_client
        if len([m for m in vc.channel.members if not m.bot]) == 0:
            await asyncio.sleep(10)
            if len([m for m in vc.channel.members if not m.bot]) == 0:
                await vc.disconnect()
                print("🚪 Left the voice channel because it was empty.")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Handles track end event, checking queue per guild."""
        if not payload.player:
            return
    
        player = payload.player
        guild_id = player.guild.id
    
        if not player.queue.is_empty:
            next_track = await player.queue.get_wait()
            await player.play(next_track)
            print(f"🎵 Now playing in {guild_id}: {next_track.title}")
        else:
            print(f"🛑 Queue is empty in {guild_id}. Leaving in 5 minutes if inactive.")
            await asyncio.sleep(300)
    
            if not player.playing and player.connected:
                player.queue.clear()
                await player.disconnect()
                del self.players[guild_id]
                print(f"🚪 Left voice channel in {guild_id} due to inactivity.")


    SEARCH_TIMEOUT = 30

    @music.command(name="play", description="Search for a song by name or enter a direct link.")
    @option("type", str, description="What do you want to search by?", choices=("Name", "Link"))
    @option("query", str, description="The name/link of the song")
    @commands.guild_only()
    async def play(self, ctx: discord.ApplicationContext, type: str, query: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond("❌ You must be in a voice channel!", ephemeral=True)

        node = wavelink.Pool.get_node()
        if node is None:
            return await ctx.respond("❌ Lavalink is not connected.", ephemeral=True)

        await ctx.defer()

        try:
            if type == "Name":
                selected_track = await self._search_and_select_track(ctx, query)
                if not selected_track:
                    return
            elif type == "Link":
                tracks = await wavelink.Pool.fetch_tracks(query)
                if not tracks:
                    return await ctx.respond("❌ Invalid or unsupported link.", ephemeral=True)
                selected_track = tracks[0]
        except Exception as e:
            return await ctx.followup.send(f"❌ An error occurred while processing your request: `{e}`")

        lock = self.guild_locks.setdefault(ctx.guild.id, asyncio.Lock())

        async with lock:
            vc: wavelink.Player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

            if not vc.playing and vc.queue.count == 0:
                await vc.play(selected_track)
                await ctx.followup.send(f"🎵 **Now playing:** [{selected_track.title}]({selected_track.uri}) by `{selected_track.author}`")
            else:
                await vc.queue.put_wait(selected_track)
                await ctx.followup.send(f"🎶 **Queued:** [{selected_track.title}]({selected_track.uri}) by `{selected_track.author}` (position: {vc.queue.count})")
            
    @music.command(name="skip", description="Skips the current song")
    async def skip_command(self, ctx: discord.ApplicationContext):
        vc: wavelink.Player = ctx.voice_client
        if not vc or not vc.playing:
            return await ctx.respond("❌ No music is currently playing.", ephemeral=True)

        if vc.queue.is_empty:
            await vc.stop()
            return await ctx.respond("⏹️ No more songs in queue. Stopping playback.")

        await vc.stop()
        await ctx.respond("⏭️ Skipped to the next song.")

    @music.command(name="stop", description="Stops the music")
    async def stop_command(self, ctx: discord.ApplicationContext):
        vc: wavelink.Player = ctx.voice_client
        if not vc or not vc.playing:
            return await ctx.respond("❌ No music is currently playing.", ephemeral=True)

        vc.queue.clear()
        await vc.stop()
        await ctx.respond("⏹️ Music stopped and queue cleared.")

    @music.command(name="queue", description="Shows the current music queue with pagination.")
    async def queue_command(self, ctx: discord.ApplicationContext):
        """Shows the current queue with pagination buttons."""
        vc: wavelink.Player = ctx.voice_client

        if not vc or not vc.queue or vc.queue.count == 0:
            return await ctx.respond("📭 **The queue is empty!**", ephemeral=True)

        queue = list(vc.queue)
        per_page = 15
        total_pages = (len(queue) - 1) // per_page + 1

        def create_queue_embed(page: int):
            start = page * per_page
            end = start + per_page
            tracks = queue[start:end]

            queue_list = "\n".join(f"`{start + i + 1}.` **{t.title}** - {t.author}" for i, t in enumerate(tracks))
            embed = discord.Embed(
                title="🎵 **Music Queue**",
                description=queue_list or "No more songs in queue.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Page {page + 1}/{total_pages}")
            return embed

        async def update_queue_message(interaction: discord.Interaction, page: int):
            """Updates the queue message when buttons are clicked."""
            if page < 0 or page >= total_pages:
                return

            embed = create_queue_embed(page)
            await interaction.response.edit_message(embed=embed, view=create_queue_view(page))

        def create_queue_view(page: int):
            view = View()

            async def go_back(interaction: discord.Interaction):
                await update_queue_message(interaction, page - 1)

            async def go_next(interaction: discord.Interaction):
                await update_queue_message(interaction, page + 1)

            if page > 0:
                back_button = Button(label="Back", style=discord.ButtonStyle.primary)
                back_button.callback = go_back
                view.add_item(back_button)

            if page < total_pages - 1:
                next_button = Button(label="Next", style=discord.ButtonStyle.primary)
                next_button.callback = go_next
                view.add_item(next_button)

            return view


        embed = create_queue_embed(0)
        await ctx.respond(embed=embed, view=create_queue_view(0))

def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))