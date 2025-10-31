import discord

class supportButtons(discord.ui.View):
    def __init__(self, embed: discord.Embed, bot: discord.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed = embed

    @discord.ui.button(label="Approve", custom_id="approve", style=discord.ButtonStyle.primary, emoji="✅")
    async def approve(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = self.bot.get_channel(1359590532854186186)
        self.embed.color = discord.Color.green()
        await channel.send(embed=self.embed)
        await interaction.message.delete()
        await interaction.response.send_message("Bug report approved", ephemeral=True)

    @discord.ui.button(label="Decline", custom_id="decline", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Bug report declined", ephemeral=True)