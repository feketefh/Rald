import discord
from discord import SlashCommandGroup
from discord import option
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
from discord.ui import Modal
from typing import Union
import json

from modules.bugReport import bugReport

with open('data/goodbyeData.json', 'r') as jsonData:
	data = json.load(jsonData)

        
class wEmbedModal(discord.ui.Modal):
	def __init__(self, title: str):
		super().__init__(title=title)
		self.title = title

		self.add_item(discord.ui.InputText(label="Title", style=discord.InputTextStyle.short))
		self.add_item(discord.ui.InputText(label="Text", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		embed = discord.Embed(title=self.children[0].value, description=self.children[1].value)
		await interaction.response.edit_message(embed=embed)

class wEmbedView(discord.ui.View):
	def __init__(self, cog, modal: Modal):
		super().__init__()
		self.cog = cog
		self.modal = modal
		self.vars = {"{guild_name}": "{guild.name}",
				"{guild_id}": "{guild.id}",
				"{member_count}": "{guild.member_count}",
				"{user_name}": "{member.name}",
				"{user_id}": "{member.id}"}
     
	@discord.ui.select(placeholder="What do you want to do?", options=[
		discord.SelectOption(label="Edit embed", value="edit"),
		discord.SelectOption(label="End setup & Save", value="done")
	])

	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
		if select.values[0] == "edit":
			#embed = discord.Embed(title=self.modal.children[0].value, description=self.modal.children[1].value)
			modal = wEmbedModal(title="Goodbye message - Embed")
			await interaction.response.send_modal(modal)

		else:
			channel = interaction.channel
			self.saveData(self.modal.children[0].value, self.modal.children[1].value, channel, "Embed")
			embed = discord.Embed(title=self.modal.children[0].value, description=self.modal.children[1].value)
			await interaction.response.edit_message(content="Setup complete", embed=embed, view=None)
	
	async def saveData(self, title, message, channel: discord.TextChannel, type):
		data[str(channel.id)] = {
			"type": type,
			"mode": "On",
			"title": title,
			"message": message,
		}
		with open("data/goodbyeData.json", 'w') as jsonFile:
			json.dump(data, jsonFile, indent=4)

class wTextModal(discord.ui.Modal):
	def __init__(self, title: str):
		super().__init__(title=title)
		self.title = title

		self.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.edit_message(content=self.children[0].value)

class wTextView(discord.ui.View):
	def __init__(self, cog, modal: Modal):
		super().__init__()
		self.cog = cog
		self.modal = modal
		self.vars = {"{guild_name}": "{guild.name}",
				"{guild_id}": "{guild.id}",
				"{member_count}": "{guild.member_count}",
				"{user_name}": "{member.name}",
				"{user_id}": "{member.id}"}

	@discord.ui.select(placeholder="What do you want to do?", options=[
		discord.SelectOption(label="Edit text", value="edit"),
		discord.SelectOption(label="End setup & Save", value="done")
	])

	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
		if select.values[0] == "edit":
			modal = wTextModal(title="Goodbye message - Text")
			await interaction.response.send_modal(modal)

		else:
			channel = interaction.channel
			self.saveData(self.modal.children[0].value, channel, "Text")
			await interaction.response.edit_message(content="Setup complete", embed=None, view=None)

	async def saveData(self, message, channel: discord.TextChannel, type):
		for key, val in self.vars.items():
			message = message.replace(key, val)

		data[str(channel.id)] = {
			"type": type,
			"mode": "On",
			"message": message,   # Both for text/embed
		}
		with open("data/goodbyeData.json", 'w') as jsonFile:
			json.dump(data, jsonFile, indent=4)


class goodbye(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.vars = {"{guild_name}": "The name of your server",
				"{guild_id}": "The ID of your server",
				"{member_count}": "The number of members in your server",
				"{user_name}": "The name of the user",
				"{user_id}": "The ID of the user"}

	goodbye = discord.SlashCommandGroup("godbye", "Goodbye system")

	@commands.Cog.listener()
	async def on_member_leave(self, member: discord.Member):
		for channel_id, config in data.items():
			if config.get("mode") != "On":
				continue

			channel = self.bot.get_channel(int(channel_id))
			if not channel:
				continue

			message = config.get("message", "Goodbye!")

			vars = {
				"{guild_name}": member.guild.name,
				"{guild_id}": str(member.guild.id),
				"{member_count}": str(member.guild.member_count),
				"{user_name}": member.name,
				"{user_id}": str(member.id)
			}
			for key, val in vars.items():
				message = message.replace(key, val)

			if config.get("type") == "Text":
				await channel.send(message)
			else:
				title = config.get("title", "Goodbye!")
				embed = discord.Embed(title=title, description=message, color=discord.Colour.green())
				await channel.send(embed=embed)

		
	@goodbye.command(name="settings", description="Setup goodbye message")
	@has_permissions(administrator=True)
	@option("type", description="Embed or text message", choices=["Embed", "Text"] )
	@option("channel", Union[discord.TextChannel], description="Channel to send message")
	@option("mode", description="Turn On/Off goodbye message in the channel", choices=["On", "Off"])
	async def settings(self, ctx: discord.ApplicationContext, type: str, channel: Union[discord.TextChannel], mode: str):
		if mode == "On":	
			if type == "Text":
				modal = discord.ui.Modal(title="Goodbye message - Text")
				modal.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

				async def modal_callback(interaction: discord.Interaction):
					await interaction.response.send_message(modal.children[0].value)

				modal.callback = modal_callback
				await ctx.send_modal(modal, ephemeral=True)
			else:

				modal = discord.ui.Modal(title="Goodbye message - Embed")
				modal.add_item(discord.ui.InputText(label="Title", style=discord.InputTextStyle.short))
				modal.add_item(discord.ui.InputText(label="Text", style=discord.InputTextStyle.long))

				async def modal_callback(interaction: discord.Interaction):
					embed = discord.Embed(title=modal.children[0].value, description=modal.children[1].value)
					await interaction.response.send_message(embed=embed, view=wEmbedView(self, modal), ephemeral=True)

				modal.callback = modal_callback
				await ctx.send_modal(modal)
		else:
			data[str(channel)]["mode"] = "Off"
			with open("data.json", 'w') as jsonFile:
				json.dump(data, jsonFile, indent=4)
				await ctx.respond("Goodbye message turned off in the channel")

	@settings.error
	async def settings_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		if isinstance(error, MissingPermissions):
			await ctx.respond("You don't have permission to use this command.", ephemeral=True)
		else:
			bugReport.sendReport("goodbye", "settings", str(error))
			await ctx.respond("An error occurred while setting up the goodbye message. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

	@goodbye.command(name="info", description="Get information about the godbye system")
	async def info(self, ctx: discord.ApplicationContext):
		embed = discord.Embed(title="Godbye System Info", color=discord.Colour.blue())
		embed.add_field(
		    name="Variables:", 
		    value="\n".join(f"{k}: {v}" for k, v in self.vars.items()), 
		    inline=False
		)
		embed.add_field(name="Example:", value="Hello {user_name}, goodbye to {guild_name}!", inline=False)
		await ctx.respond(embed=embed, ephemeral=True)

	@info.error
	async def info_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		if isinstance(error, discord.ApplicationCommandInvokeError):
			bugReport.sendReport("goodbye", "info", str(error))
			await ctx.respond("An error occurred while getting the goodbye system info. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
			

def setup(bot: discord.Bot):
	bot.add_cog(goodbye(bot))