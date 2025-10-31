import discord
from discord import ui, Interaction, SelectOption, Embed, Colour

def get_commands_by_cog(bot: discord.Bot):
    """Return a dict of cog names and unique, visible commands (no group-level or duplicates)."""
    cog_commands = {}

    for command in bot.walk_application_commands():
        if getattr(command, "hidden", False):
            continue

        if isinstance(command, discord.SlashCommandGroup):
            for sub in command.subcommands:
                if getattr(sub, "hidden", False):
                    continue
                cog_name = sub.cog.__class__.__name__ if sub.cog else "Uncategorized"
                cog_commands.setdefault(cog_name, []).append(sub)

        elif isinstance(command, discord.SlashCommand) and command.parent is None:
            cog_name = command.cog.__class__.__name__ if command.cog else "Uncategorized"
            cog_commands.setdefault(cog_name, []).append(command)

    return cog_commands

class HelpView(ui.View):
    def __init__(self, bot: discord.Bot, author: discord.User):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author
        self.cog_commands = get_commands_by_cog(bot)

        options = [
            SelectOption(
                label=cog,
                description=f"{len(commands)} command(s)",
                value=cog
            )
            for cog, commands in self.cog_commands.items()
            if commands
        ]

        if not options:
            self.add_item(ui.Button(label="No commands found", disabled=True))
            return

        self.select = ui.Select(
            placeholder="Select a category...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        selected_cog = self.select.values[0]
        commands = self.cog_commands.get(selected_cog, [])

        embed = Embed(
            title=f"{selected_cog} Commands",
            description=f"List of commands in the `{selected_cog}` category:",
            color=Colour.random()
        )
        for command in commands:
            embed.add_field(
                name=f"/{command.qualified_name}",
                value=command.description or "No description.",
                inline=False
            )

        embed.set_footer(text=f"Requested by {self.author.name}")
        embed.set_thumbnail(url=self.bot.user.avatar)
        await interaction.response.edit_message(embed=embed, view=self)