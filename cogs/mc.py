import discord
from discord.commands import SlashCommandGroup
from discord.ext import tasks, commands
from discord import option
from discord.ext.commands import has_permissions, MissingPermissions

from typing import Union
import requests
import json
import time
import os

from modules.bugReport import bugReport

with open('data/mcData.json', 'r') as jsonData:
    data = json.load(jsonData)

class BedrockSelect(discord.ui.Select):
    def __init__(self, channel):
        self.channel = channel
        options = [
            discord.SelectOption(label="Setup Bedrock", description="Setup Bedrock status as well"),
            discord.SelectOption(label="End setup", description="End setup and make everything live")
        ]
        super().__init__(placeholder="Select the action", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Setup Bedrock":
            modal = bedrockModal(title="Enter the IP of your server", channel=self.channel, final=True)
            await interaction.response.send_modal(modal)
        else:
            embed = discord.Embed(title="Minecraft status channel setup", description="Setup complete!")
            await interaction.response.edit_message(embed=embed, view=None)


class JavaSelect(discord.ui.Select):
    def __init__(self, channel):
        self.channel = channel
        options = [
            discord.SelectOption(label="Setup Java", description="Setup Java status as well"),
            discord.SelectOption(label="End setup", description="End setup and make everything live")
        ]
        super().__init__(placeholder="Select the action", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Setup Java":
            modal = javaModal(title="Enter the IP of your server", channel=self.channel, final=True)
            await interaction.response.send_modal(modal)
        else:
            embed = discord.Embed(title="Minecraft status channel setup", description="Setup complete!")
            await interaction.response.edit_message(embed=embed, view=None)


class finalView(discord.ui.View):
    def __init__(self, channel: discord.TextChannel, type: str):
        super().__init__()
        self.channel = channel
        self.type = type

        if self.type == "bedrock":
            self.add_item(BedrockSelect(self.channel))
        else:
            self.add_item(JavaSelect(self.channel))


class javaModal(discord.ui.Modal):
    def __init__(self, title: str, channel: discord.TextChannel, final: bool):
        super().__init__(title=title)
        self.title = title
        self.channel = channel
        self.final = final

        self.add_item(discord.ui.InputText(label="IP", placeholder="Enter the IP of your server"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # First and only allowed response method

        res = requests.get(f"https://api.mcstatus.io/v2/status/java/{self.children[0].value}")
        mcData = res.json()

        if not mcData.get("online", False):
            embed = discord.Embed(
                title="❌ Minecraft Java Server Offline",
                description=f"The server at `{self.children[0].value}` appears to be offline.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="✅ Minecraft Java Server Status",
                description=f"Host: {self.children[0].value}\nIP: {mcData.get('ip_address', 'N/A')}:{mcData.get('port', 'N/A')}",
                color=discord.Color.green()
            )
            embed.add_field(name="EULA Blocked", value=str(mcData.get("eula_blocked", "N/A")), inline=True)

            version = mcData.get("version", {}).get("name_clean", "Unknown")
            embed.add_field(name="Version", value=version, inline=True)

            players = mcData.get("players", {})
            online = players.get("online", "N/A")
            max_players = players.get("max", "N/A")
            embed.add_field(name="Players", value=f"{online}/{max_players}", inline=True)

            motd = mcData.get("motd", {}).get("clean", "N/A")
            embed.add_field(name="MOTD", value=motd, inline=False)

            embed.set_image(url=f"https://api.mcstatus.io/v2/widget/java/{self.children[0].value}")

        message = await self.channel.send(embed=embed)

        channel_id = str(self.channel.id)
        message_id = str(message.id)

        if channel_id not in data:
            data[channel_id] = {}

        data[channel_id]["java"] = {
            "ip": self.children[0].value,
            "mode": "On",
            "message": message_id
        }

        with open("data/mcData.json", "w") as f:
            json.dump(data, f, indent=4)

        if self.final == False:
            sembed = discord.Embed(
                title="Minecraft status channel setup",
                description="Set up Bedrock server status as well or end the setup?"
            )
            await interaction.edit_original_response(embed=sembed, view=finalView(self.channel, "bedrock"))
        else:
            sembed = discord.Embed(
                title="Minecraft status channel setup",
                description="Setup complete!"
            )
            await interaction.edit_original_response(embed=sembed, view=None)


class bedrockModal(discord.ui.Modal):
    def __init__(self, title: str, channel: discord.TextChannel, final: bool):
        super().__init__(title=title)
        self.title = title
        self.channel = channel
        self.final = final

        self.add_item(discord.ui.InputText(label="IP", placeholder="Enter the IP of your server"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        res = requests.get(f"https://api.mcstatus.io/v2/status/bedrock/{self.children[0].value}")
        mcData = res.json()

        if not mcData.get("online", False):
            embed = discord.Embed(
                title="❌ Minecraft Bedrock Server Offline",
                description=f"The server at `{self.children[0].value}` appears to be offline.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="✅ Minecraft Bedrock Server Status",
                description=f"Host: {self.children[0].value}\nIP: {mcData.get('ip_address', 'N/A')}:{mcData.get('port', 'N/A')}",
                color=discord.Color.green()
            )

            embed.add_field(name="EULA Blocked", value=str(mcData.get("eula_blocked", "N/A")), inline=True)

            version = mcData.get("version", {}).get("name", "Unknown")
            embed.add_field(name="Version", value=version, inline=True)

            players = mcData.get("players", {})
            online = players.get("online", "N/A")
            max_players = players.get("max", "N/A")
            embed.add_field(name="Players", value=f"{online}/{max_players}", inline=True)

            motd = mcData.get("motd", {}).get("clean", "N/A")
            embed.add_field(name="MOTD", value=motd, inline=False)

            embed.set_image(url=f"https://api.mcstatus.io/v2/widget/bedrock/{self.children[0].value}")

        message = await self.channel.send(embed=embed)

        channel_id = str(self.channel.id)
        message_id = str(message.id)
        if channel_id not in data:
            data[channel_id] = {}
            with open("data/mcData.json", "w") as f:
                json.dump(data, f, indent=4) 
        data[channel_id]["bedrock"] = {
            "ip": self.children[0].value,
            "mode": "On",
            "message": message_id
        }
        with open("data/mcData.json", "w") as f:
            json.dump(data, f, indent=4)
        if self.final == False:
            sembed = discord.Embed(title="Minecraft staus channel setup", description=f"So you wan to set up Java server status as well or end the setup?")
            await interaction.edit_original_response(embed=sembed, view=finalView(self.channel, "java"))
        else:
            embed = discord.Embed(title="Minecraft status channel setup", description="Setup complete!")
            await interaction.edit_original_response(embed=embed, view=None)

class TurnOffSelector(discord.ui.View):
    def __init__(self, channel_id, data, channel: discord.TextChannel):
        super().__init__(timeout=60)
        self.channel_id = channel_id
        self.data = data
        self.channel = channel

        active = [stype for stype, info in data[channel_id].items() if info["mode"] == "On"]

        if len(active) > 25:
            active = active[:25]

        options = [discord.SelectOption(label=stype.capitalize(), value=stype) for stype in active]

        select = discord.ui.Select(
            placeholder="Select server types to turn off",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="turn_off_select"
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        for stype in interaction.data["values"]:
            try:
                msg_id = int(self.data[self.channel_id][stype]["message"])
                message = await self.channel.fetch_message(msg_id)
                await message.delete()
                self.data[self.channel_id][stype]["mode"] = "Off"
            except Exception as e:
                print(f"Failed to turn off {stype}: {e}")

        with open("data/mcData.json", 'w') as jsonFile:
            json.dump(self.data, jsonFile, indent=4)

        await interaction.response.edit_message(content="Selected server status types turned off.", view=None)


class skinView(discord.ui.View):
    def __init__(self, uuid: str, username: str):
        super().__init__()
        self.uuid = uuid
        self.username = username

        self.add_item(discord.ui.Button(
            label="Download Skin",
            style=discord.ButtonStyle.link,
            url=f"https://api.mineatar.io/skin/{self.uuid}?download=true&format=png",
            row=1
        ))


    async def update_buttons(self, clicked_button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.style != discord.ButtonStyle.link:
                child.disabled = (child == clicked_button)

    @discord.ui.button(label="Full", custom_id="full", style=discord.ButtonStyle.primary, disabled=True, row=0)
    async def full_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Skin of {self.username}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://api.mineatar.io/head/{self.uuid}")
        embed.set_image(url=f"https://api.mineatar.io/body/full/{self.uuid}")
        await self.update_buttons(button)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Front side", custom_id="front", style=discord.ButtonStyle.primary, row=0)
    async def front_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Skin of {self.username}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://api.mineatar.io/head/{self.uuid}")
        embed.set_image(url=f"https://api.mineatar.io/body/front/{self.uuid}")
        await self.update_buttons(button)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Back side", custom_id="back", style=discord.ButtonStyle.primary, row=0)
    async def back_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Skin of {self.username}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://api.mineatar.io/head/{self.uuid}")
        embed.set_image(url=f"https://api.mineatar.io/body/back/{self.uuid}")
        await self.update_buttons(button)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Right side", custom_id="right", style=discord.ButtonStyle.primary, row=0)
    async def right_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Skin of {self.username}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://api.mineatar.io/head/{self.uuid}")
        embed.set_image(url=f"https://api.mineatar.io/body/right/{self.uuid}")
        await self.update_buttons(button)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Left side", custom_id="left", style=discord.ButtonStyle.primary, row=0)
    async def left_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Skin of {self.username}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://api.mineatar.io/head/{self.uuid}")
        embed.set_image(url=f"https://api.mineatar.io/body/left/{self.uuid}")
        await self.update_buttons(button)
        await interaction.response.edit_message(embed=embed, view=self)


class mcStatus(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    @discord.ui.select(placeholder="Select the type of server",
                        options=[discord.SelectOption(label="Java", description="Pick if your server is a Java server"), discord.SelectOption(label="Bedrock", description="Pick if your server is a Bedrock server")],
                        min_values=1,
                        max_values=1)
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "Java":
            modal = javaModal(title="Enter the IP of your server", channel=self.channel, final=False)
            await interaction.response.send_modal(modal)

        else:
            modal = bedrockModal(title="Enter the IP of your server", channel=self.channel, final=False)
            await interaction.response.send_modal(modal)


class mc(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.update_minecraft_status.start()
    
    mc = discord.SlashCommandGroup("mc", "Minecraft commands")

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