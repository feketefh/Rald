import discord
from discord.ext import tasks, commands
from discord import option
from discord.ext.commands import has_permissions, MissingPermissions

from typing import Union
import requests
import json

from modules.bugReport import bugReport
from modules import subCommands
from modules.mcViews import mcStatus, skinView, TurnOffSelector

with open('data/mcData.json', 'r') as jsonData:
    data = json.load(jsonData)

class mc(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.update_minecraft_status.start()
    
    mc = subCommands.mc

    @tasks.loop(minutes=5)
    async def update_minecraft_status(self):
        with open("data/mcData.json", "r") as jsonFile:
            data = json.load(jsonFile)

        for channel_id, server_data in list(data.items()):
            channel = self.bot.get_channel(int(channel_id))
            if channel is None:
                del data[channel_id]
                with open("data/mcData.json", 'w') as jsonFile:
                    json.dump(data, jsonFile, indent=4)
                continue

            for server_type, info in server_data.items():
                if info.get("mode") == "Off":
                    continue

                try:
                    message_id = int(info["message"])
                    message = await channel.fetch_message(message_id)

                    ip = info["ip"]
                    url = f"https://api.mcstatus.io/v2/status/{server_type}/{ip}"
                    res = requests.get(url)
                    mcData = res.json()

                    if not mcData.get("online", False):
                        embed = discord.Embed(
                            title=f"❌ Minecraft {server_type.capitalize()} Server Offline",
                            description=f"The server at `{ip}` appears to be offline.",
                            color=discord.Color.red()
                        )
                    else:
                        ip_display = f"{mcData.get('ip_address', 'N/A')}:{mcData.get('port', 'N/A')}" if server_type != "bedrock" else mcData.get('ip_address', 'N/A')
                        embed = discord.Embed(
                            title=f"✅ Minecraft {server_type.capitalize()} Server Status",
                            description=f"Host: {ip}\nIP: {ip_display}",
                            color=discord.Color.green()
                        )

                        embed.add_field(name="EULA Blocked", value=str(mcData.get("eula_blocked", "N/A")), inline=True)

                        if "version" in mcData:
                            if server_type == "bedrock":
                                embed.add_field(name="Version", value=mcData["version"].get("name", "Unknown"), inline=True)
                            else:
                                embed.add_field(name="Version", value=mcData["version"].get("name_clean", "Unknown"), inline=True)

                        players = mcData.get("players", {})
                        embed.add_field(
                            name="Players",
                            value=f"{players.get('online', 'N/A')}/{players.get('max', 'N/A')}",
                            inline=True
                        )

                        motd = mcData.get("motd", {}).get("clean", "N/A")
                        embed.add_field(name="MOTD", value=motd, inline=False)

                        embed.set_image(url=f"https://api.mcstatus.io/v2/widget/{server_type}/{ip}")

                    await message.edit(embed=embed)

                except discord.NotFound:
                    del data[channel_id][server_type]
                except Exception as e:
                    await channel.send(f"⚠️ An error occurred while updating `{server_type}` server: `{e}`")



    @mc.command(name="status", description="Get information about a Minecraft server")
    @option("type", str, description="The type of the server", choices=["Java", "Bedrock"])
    @option("ip", str, description="The IP of the server")
    async def status(self, ctx: discord.ApplicationContext, type: str, ip: str):
        await ctx.defer()

        if type == "Java":
            try:
                res = requests.get(f"https://api.mcstatus.io/v2/status/java/{ip}")
                mcData = res.json()
                embed = discord.Embed(title="Minecraft Java Server Status", description=f"Host: {ip}\nIP: {mcData['ip_address']}:{mcData['port']}")
                embed.add_field(name="EULA Blocked", value=str(mcData["eula_blocked"]))
                embed.add_field(name="Version", value=mcData["version"]["name_clean"])
                embed.add_field(name="Players", value=f"{mcData['players']['online']}/{mcData['players']['max']}")
                embed.add_field(name="MOTD", value=mcData["motd"]["clean"])
                embed.set_image(url=f"https://api.mcstatus.io/v2/widget/java/{ip}")
                await ctx.respond(embed=embed)
            except (requests.RequestException, ValueError):
                await ctx.respond("⚠️ Failed to fetch server data.", ephemeral=True)
                return
        else:
            try:
                res = requests.get(f"https://api.mcstatus.io/v2/status/bedrock/{ip}")
                mcData = res.json()
                embed = discord.Embed(title="Minecraft Bedrock Server Status", description=f"Host: {ip}\nIP: {mcData['ip_address']}:{mcData['port']}")
                embed.add_field(name="EULA Blocked", value=str(mcData["eula_blocked"]))
                embed.add_field(name="Version", value=mcData["version"]["name_clean"])
                embed.add_field(name="Players", value=f"{mcData['players']['online']}/{mcData['players']['max']}")
                embed.add_field(name="MOTD", value=mcData["motd"]["clean"])
                embed.set_image(url=f"https://api.mcstatus.io/v2/widget/bedrock/{ip}")
                await ctx.respond(embed=embed)
            except (requests.RequestException, ValueError):
                await ctx.respond("⚠️ Failed to fetch server data.", ephemeral=True)
                return

    @status.error
    async def status_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        bugReport.sendReport("mc", "status", str(error))
        await ctx.respond("An error occured while getting Minecraft server data. A bug report has been sent to the developers", ephemeral=True)

    @mc.command(name="skin", description="Get a Minecraft skin")
    @option("username", str, description="The username of the player")
    async def skin(self, ctx: discord.ApplicationContext, username: str):
        await ctx.defer()
        res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if res.status_code == 200:
            uuid = res.json()["id"]
            skin_url = f"https://api.mineatar.io/head/{uuid}"
            embed = discord.Embed(title=f"Skin of {username}", color=discord.Color.blue())
            embed.set_thumbnail(url=skin_url)
            embed.set_image(url=f"https://api.mineatar.io/body/full/{uuid}")
            await ctx.respond(embed=embed, view=skinView(uuid=uuid, username=username))
        else:
            await ctx.respond("User not found", ephemeral=True)
    
    @skin.error
    async def skin_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("mc", "skin", str(error))
            await ctx.respond("An error occurred while getting the skin. A bug report has been sent to the developers", ephemeral=True)

    @mc.command(name="statuschannel", description="Setup a channel for Minecraft server status updates")
    @has_permissions(administrator=True)
    @option("channel", Union[discord.TextChannel], description="Channel to send updates")
    @option("mode", str, description="Turn On/Off status updates in the channel", choices=["On", "Off"])
    async def statuschannel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, mode: str):
        with open("data/mcData.json", "r") as jsonFile:
            data = json.load(jsonFile)

        channel_id = str(channel.id)

        if mode == "On":
            if channel_id in data and any(server["mode"] == "On" for server in data[channel_id].values()):
                await ctx.respond("Status updates are already turned on in this channel!", ephemeral=True)
                return

            if channel_id not in data:
                data[channel_id] = {}

            embed = discord.Embed(title="Minecraft status channel setup", description="Please select the type of your server")
            await ctx.respond(embed=embed, view=mcStatus(channel), ephemeral=True)

        else:
            if channel_id not in data or all(server["mode"] == "Off" for server in data[channel_id].values()):
                await ctx.respond("Status updates are already turned off in this channel!", ephemeral=True)
                return

            active_servers = [stype for stype, info in data[channel_id].items() if info["mode"] == "On"]

            if len(active_servers) == 1:
                stype = active_servers[0]
                msg_id = int(data[channel_id][stype]["message"])
                message = await channel.fetch_message(msg_id)
                await message.delete()
                data[channel_id][stype]["mode"] = "Off"

                if all(info["mode"] == "Off" for info in data[channel_id].values()):
                    del data[channel_id]

                with open("data/mcData.json", 'w') as jsonFile:
                    json.dump(data, jsonFile, indent=4)

                await ctx.respond(f"{stype.capitalize()} status turned off in the channel.", ephemeral=True)

            elif len(active_servers) > 1:
                await ctx.respond("Choose which server status(es) to turn off:", view=TurnOffSelector(channel_id, data, channel), ephemeral=True)

    @statuschannel.error
    async def statuschannel_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, MissingPermissions):
            await ctx.respond("You don't have permission to use this command.", ephemeral=True)
        else:
            bugReport.sendReport("mc", "statuschannel", str(error))
            await ctx.respond("An error occurred while setting up the status channel. A bug report has been sent to the developers", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(mc(bot))