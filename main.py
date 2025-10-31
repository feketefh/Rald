import os
import json
import time
import discord
from discord import option
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import MissingPermissions

from modules.bugReport import bugReport
from dotenv import load_dotenv
import itertools
import datetime

intents = discord.Intents.all()
bot: commands.Bot = commands.Bot(intents=intents, command_prefix="~", owner_id=1250010803462078464)
bot.start_time = datetime.datetime.now(datetime.timezone.utc)
with open('data.json') as f:
    data: dict = json.load(f)

status_cycle = itertools.cycle([
    lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"),
    lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{sum(g.member_count for g in bot.guilds)} users"),
    lambda: discord.Activity(type=discord.ActivityType.listening, name=f"{len(bot.application_commands)} commands")
])

async def sync_all():
    await bot.sync_commands(guild_ids=[g.id for g in bot.guilds])

async def handle_cog(ctx: discord.ApplicationContext, action: str, cog_name: str):
    try:
        if action == "load":
            bot.load_extension(f'cogs.{cog_name}')
        elif action == "unload":
            bot.unload_extension(f'cogs.{cog_name}')
        elif action == "reload":
            bot.unload_extension(f'cogs.{cog_name}')
            bot.load_extension(f'cogs.{cog_name}')
        await sync_all()
        await ctx.respond(f"Cog {action}ed: {cog_name}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    for cogs in data['cogs']:
        bot.load_extension(f'cogs.{cogs}')
        print(f"Loaded Cog: {cogs}")
    await bot.sync_commands(guild_ids=[guild.id for guild in bot.guilds])
    update_status.start()
    print("----------")
    print(f"   {bot.user.name}  ")
    print("----------")

@tasks.loop(seconds=60)
async def update_status():
    status_func = next(status_cycle)
    await bot.change_presence(activity=status_func())

@bot.event
async def on_guild_join(guild: discord.Guild):
    await bot.sync_commands(guild_ids=[guild.id])


@bot.command()
@commands.is_owner()
async def cog(interaction: discord.Interaction, action: str = None, cog: str = None):
    if action in ["load", "unload", "reload"] and cog:
        await handle_cog(interaction, action, cog)
    elif action == "list":
        with open('data.json') as f:
            data: dict = json.load(f)
        cogs = ', '.join(data['cogs'])
        await interaction.response.send_message(f"Cogs: {cogs}", ephemeral=True)
    else:
        await interaction.response.send_message("Use the subcommands: load, unload, reload, list", delete_after=10)


load_dotenv(dotenv_path=".env")
token: str = os.getenv("TOKEN")
if token is None:
    raise ValueError("Bot token not found in environment. Make sure .env is set correctly.")

bot.run(token)