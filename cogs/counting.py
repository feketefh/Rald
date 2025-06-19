import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import option
from discord.ext.commands import has_permissions, MissingPermissions, BotMissingPermissions

from typing import Union
import asyncio
import json
import os

from modules.bugReport import bugReport

class Counting(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    counting = discord.SlashCommandGroup("counting", "Counting commands")

    async def saveData(self, data):
        async with self.lock:
            with open('data/countingData.json', 'w') as jsonData:
                json.dump(data, jsonData, indent=4)
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        with open('data/countingData.json', 'r') as jsonData:
            data = json.load(jsonData)
        channel_id = str(message.channel.id)

        if channel_id in data and data[channel_id].get("mode") == "On":
            if message.content.isdigit():
                current_number = int(message.content)

                last_number = data[channel_id].get("last_number", 0)

                if current_number == last_number + 1:
                    data[channel_id]["last_number"] = current_number
                    await self.saveData(data)
                    await message.add_reaction("✅")
                else:
                    data[channel_id]["last_number"] = 0
                    await self.saveData(data)
                    await message.add_reaction("❌")
                    embed = discord.Embed(title="Counting", description=f"{message.author} ruined at {data[channel_id]["last_number"]}.\nGame starts over from 0.", color=discord.Color.orange())
                    await message.channel.send(embed=embed)


    @counting.command(name="setup", description="Setup counting")
    @has_permissions(administrator=True)
    @option("channel", Union[discord.TextChannel], description="Channel to count in", required=True)
    @option("mode", str, description="Turn On/Off counting in the channel", choices=["On", "Off", "Reset"])
    async def start(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, mode: str):
        channel_id = str(channel.id)
        with open('data/countingData.json', 'r') as jsonData:
            data = json.load(jsonData)
        if mode == "On":
            if channel_id in data and data[channel_id].get("mode") == "On":
                await ctx.respond("Counting is already turned on in this channel!", ephemeral=True)
                return
            
            if channel not in data:
                data[channel_id] = {
                    "mode": "On",
                    "last_number": 0
                }

            data[channel_id]["mode"] = "On"
            await self.saveData(data)

            embed = discord.Embed(title="Counting", description=f"Counting started in {channel.mention}", color=discord.Color.green())
            await ctx.respond(embed=embed)
            await channel.send(f"<:check:1368599528604831755> Counting has started. The game starts from {data[channel_id]["last_number"]}.")
        elif mode == "Off":
            if channel_id not in data or data[channel_id]["mode"] == "Off":
                await ctx.respond("Counting is already turned off in this channel!", ephemeral=True)
                return

            data[channel_id]["mode"] = "Off"
            await self.saveData(data)

            embed = discord.Embed(title="Counting", description=f"Counting stopped in {channel.mention}", color=discord.Color.red())
            await ctx.respond(embed=embed)

            await channel.send("<:cross:1368599505343090808> Counting has been stopped.")

        elif mode == "Reset":
            if channel_id not in data:
                await ctx.respond("Firstly please setup counting with the ``/counting setup``.", ephemeral=True)
                return

            data[channel_id]["last_number"] = 0
            await self.saveData(data)

            embed = discord.Embed(title="Counting", description=f"Counting reset in {channel.mention}", color=discord.Color.dark_orange())
            await ctx.respond(embed=embed)
            await channel.send(f"<:loop:1368602781635838053> Counting has been reset. The game starts over from 0.")

    @start.error
    async def start_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, BotMissingPermissions):
            await ctx.respond("I do not have permission to send messages in this channel.", ephemeral=True)
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("counting", "setup", str(error))
            await ctx.respond("An error occurred while setting up counting. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(Counting(bot))