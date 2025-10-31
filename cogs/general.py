import discord
from discord import Embed, Colour
from discord.ext import commands

import datetime
import psutil
import platform

from modules.bugReport import bugReport
from modules import subCommands
from modules import generalHelp


class General(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    general = subCommands.general

    @general.command(name="help", description="Shows help menu")
    async def help(self, ctx: discord.ApplicationContext):
        embed = Embed(
            title="Help Menu",
            description="Use the select menu below to browse commands by category.",
            color=Colour.random()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=self.bot.user.avatar)

        view = generalHelp.HelpView(self.bot, ctx.author)
        await ctx.respond(embed=embed, view=view)

    @help.error
    async def help_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, discord.DiscordException):
            bugReport.sendReport("general", "help", str(error))
            await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @general.command(name="ping", description="Pong")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f'🏓Pong! {round(self.bot.latency * 1000)}ms')

    @ping.error
    async def ping_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, discord.DiscordException):
            bugReport.sendReport("general", "ping", str(error))
            await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @general.command(name="botinfo", description="Displays information about the bot")
    async def botinfo(self, ctx: discord.ApplicationContext):
        owner = self.bot.get_user(ctx.bot.owner_id) or await self.bot.fetch_user(ctx.bot.owner_id)
        ping = round(self.bot.latency * 1000)
        library = "Py-cord"
        guild_count = len(self.bot.guilds)
        user_count = sum(1 for _ in self.bot.get_all_members())
        process = psutil.Process()
        ram_usage = f"{process.memory_info().rss / (1024 * 1024):.2f} MB"
        command_count = len(self.bot.commands)

        # Uptime
        def get_uptime(start_time):
            now = datetime.datetime.utcnow()
            delta = now - start_time
            days, remainder = divmod(delta.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

        uptime = get_uptime(self.bot.start_time)
        python_version = platform.python_version()
        os_info = f"{platform.system()} {platform.release()}"

        embed = discord.Embed(title="🤖 Bot Information", color=discord.Colour.blue())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        embed.add_field(name="Owner:", value=str(owner), inline=False)
        embed.add_field(name="Ping:", value=f"{ping} ms", inline=True)
        embed.add_field(name="Guilds:", value=f"{guild_count}", inline=True)
        embed.add_field(name="Commands:", value=f"{command_count}", inline=True)
        embed.add_field(name="Users:", value=f"{user_count}", inline=True)
        embed.add_field(name="RAM Usage:", value=ram_usage, inline=True)
        embed.add_field(name="Uptime:", value=uptime, inline=True)
        embed.add_field(name="Python Version:", value=python_version, inline=True)
        embed.add_field(name="OS:", value=os_info, inline=True)
        embed.add_field(name="Library:", value=library, inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1345731207866089605/e42f77dad8958d6d48a1ec3cf11100db.webp?size=512")
        embed.set_image(url="https://cdn.discordapp.com/banners/1345731207866089605/ffd20f17f8158264767795535dba1e3c.webp?size=512")

        await ctx.respond(embed=embed)


    @botinfo.error
    async def botinfo_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, discord.DiscordException):
            bugReport.sendReport("general", "botinfo", str(error))
            await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(General(bot))