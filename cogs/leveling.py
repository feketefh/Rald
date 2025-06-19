import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import option

from typing import Union
import json
import os

from modules.bugReport import bugReport

with open('data/countingData.json', 'r') as jsonData:
    data = json.load(jsonData)

class leveling(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    leveling = discord.SlashCommandGroup("leveling", "Leveling commands")


def setup(bot: discord.Bot):
    bot.add_cog(leveling(bot))