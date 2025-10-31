import discord
from discord.ui import Modal

import json


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