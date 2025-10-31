import discord
from discord.ext import commands

from modules.bugReport import bugReport
from modules import subCommands
from modules.supportView import supportButtons


class support(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    support = subCommands.support

    @support.command(name="bugreport", description="Report a bug")
    async def bugreport(self, ctx: discord.ApplicationContext):
        modal = discord.ui.Modal(title="Bugreport")
        modal.add_item(discord.ui.InputText(label="Title", style=discord.InputTextStyle.short))
        modal.add_item(discord.ui.InputText(label="Short description", style=discord.InputTextStyle.short))
        modal.add_item(discord.ui.InputText(label="Steps to reproduce", style=discord.InputTextStyle.long))
        modal.add_item(discord.ui.InputText(label="Bugged command / feature", style=discord.InputTextStyle.short))

        async def modal_callback(interaction: discord.Interaction):
            brchannel = self.bot.get_channel(1359590496082854029)
            embed = discord.Embed(title=modal.children[0].value, description=modal.children[1].value, color=discord.Color.orange())
            embed.add_field(name="Steps to reproduce", value=modal.children[2].value)
            embed.add_field(name="Bugged command / system", value=modal.children[3].value, inline=False)
            embed.set_footer(text=f"Reported by {interaction.user.name}", icon_url=interaction.user.avatar)
            embed.set_author(name="Bug Report", icon_url=self.bot.user.avatar.url)
            await brchannel.send(embed=embed, view=supportButtons(embed=embed, bot=self.bot))
            await interaction.response.send_message("Thanks, for your bug report our team will investigate the situation in a few hours", ephemeral=True)
        modal.callback = modal_callback
        await ctx.send_modal(modal)

    @bugreport.error
    async def bugreport_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error):
            bugReport.sendReport("support", "bugreport", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(support(bot))