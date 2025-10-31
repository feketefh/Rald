import discord

import requests
import json

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