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
bot: discord.Bot = discord.Bot(intents=intents, owner_id=1250010803462078464)
bot.start_time = datetime.datetime.utcnow()
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

dev_group = discord.SlashCommandGroup("dev", "Dev commands")

@dev_group.command(name="load", description="Load a cog")
@option("cog", str, description="Which cog do you want to load?", required=True)
@commands.is_owner()
async def load_cog(ctx: discord.ApplicationContext, cog: str):
    await ctx.defer()
    await handle_cog(ctx, "load", cog)

@load_cog.error
async def load_cog_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You do not have the necessary permissions to use this command.", ephemeral=True)
    else:
        bugReport.sendReport("main", "load_cog", str(error))
        await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

@dev_group.command(name="unload", description="Unload a cog")
@option("cog", str, description="Which cog do you want to unload?", required=True)
@commands.is_owner()
async def unload_cog(ctx: discord.ApplicationContext, cog: str):
    await ctx.defer()
    await handle_cog(ctx, "unload", cog)

@unload_cog.error
async def unload_cog_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You do not have the necessary permissions to use this command.", ephemeral=True)
    else:
        bugReport.sendReport("main", "unload_cog", str(error))
        await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

@dev_group.command(name="reload", description="Reload a cog")
@option("cog", str, description="Which cog do you want to reload?", required=True)
@commands.is_owner()
async def reload_cog(ctx: discord.ApplicationContext, cog: str):
    await ctx.defer()
    await handle_cog(ctx, "reload", cog)

@reload_cog.error
async def reload_cog_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You do not have the necessary permissions to use this command.", ephemeral=True)
    else:
        bugReport.sendReport("main", "reload_cog", str(error))
        await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)


@dev_group.command(name="list", description="List all cogs")
@commands.is_owner()
async def listcogs(ctx: discord.ApplicationContext):
    with open('data.json') as f:
        data: dict = json.load(f)
    cogs = ', '.join(data['cogs'])
    await ctx.respond(f"Cogs: {cogs}")

@listcogs.error
async def listcogs_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You do not have the necessary permissions to use this command.", ephemeral=True)
    else:
        bugReport.sendReport("main", "listcogs", str(error))
        await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

bot.add_application_command(dev_group)
load_dotenv(dotenv_path=".env")
token: str = os.getenv("TOKEN")
if token is None:
    raise ValueError("Bot token not found in environment. Make sure .env is set correctly.")

bot.run(token)