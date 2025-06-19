import discord
from discord import option
from discord.ext import commands
import json
import requests
from modules.bugReport import bugReport
EMBED_STORAGE = "data/embedsData.json"
CONFIG_FILE = "data/embedConfig.json"

class EmbedEditor(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.embeds = self.load_embeds()
        self.config = self.load_config()

    def load_embeds(self):
        try:
            with open(EMBED_STORAGE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_embeds(self):
        with open(EMBED_STORAGE, "w") as f:
            json.dump(self.embeds, f, indent=4)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    editor = discord.SlashCommandGroup("embed", "Embed Editor System")

    @editor.command(name="action", description="Embed actions")
    @commands.has_permissions(administrator=True)
    @option("action", description="Use the desired action", choices=["create", "edit", "send", "delete", "share"])
    async def embed_action(self, ctx: discord.ApplicationContext, action: str):
        user_id = str(ctx.user.id)

        self.embeds = self.load_embeds()
        if action == "create":
            if user_id in self.embeds and len(self.embeds[user_id]) >= 5:
                return await ctx.respond("You reached the max number of active embeds. Please modify an already existing one!", ephemeral=True)

            modal = discord.ui.Modal(title="Create Embed")
            modal.add_item(discord.ui.InputText(label="Title", required=False))
            modal.add_item(discord.ui.InputText(label="Description", required=False))

            async def modal_callback(interaction: discord.Interaction):
                title = modal.children[0].value or ""
                description = modal.children[1].value or ""
                embed_data = {"title": title, "description": description, "fields": []}

                if user_id not in self.embeds:
                    self.embeds[user_id] = []

                self.embeds[user_id].append(embed_data)
                self.save_embeds()
                embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
                await interaction.response.send_message(embed=embed, view=EmbedEditView(self, user_id, len(self.embeds[user_id]) - 1), ephemeral=True)

            modal.callback = modal_callback
            await ctx.send_modal(modal)

        elif action == "edit":
            self.embeds = self.load_embeds()
            embed_data = self.embeds.get(user_id)
            if not embed_data:
                return await ctx.respond("You don't have embeds you could edit", ephemeral=True)
            options = [discord.SelectOption(label=f"Embed {i + 1}: {embed['title']}", value=str(i)) for i, embed in
                       enumerate(embed_data)]
            select = discord.ui.Select(placeholder="Choose an embed you want to edit!", options=options)
            async def select_callback(interaction: discord.Interaction):
                selected_index = int(select.values[0])
                selected_embed = embed_data[selected_index]
                embed = discord.Embed(
                    title=selected_embed.get("title", ""),
                    description=selected_embed.get("description", ""),
                    color=discord.Color.blue()
                )
                if "author" in selected_embed:
                    embed.set_author(
                        name=selected_embed["author"].get("name", ""),
                        icon_url=selected_embed["author"].get("icon_url", None)
                    )
                if "footer" in selected_embed:
                    embed.set_footer(
                        text=selected_embed["footer"].get("text", ""),
                        icon_url=selected_embed["footer"].get("icon_url", None)
                    )
                if "image" in selected_embed:
                    embed.set_image(url=selected_embed["image"])
                if "thumbnail" in selected_embed:
                    embed.set_thumbnail(url=selected_embed["thumbnail"])
                for field in selected_embed.get("fields", []):
                    embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
                await interaction.response.send_message(
                    embed=embed,
                    view=EmbedEditView(self, user_id, selected_index),
                    ephemeral=True
                )
            select.callback = select_callback
            await ctx.respond(view=discord.ui.View(select), ephemeral=True)


        elif action == "send":
            self.embeds = self.load_embeds()
            def is_valid_url(url):
                try:
                    response = requests.get(url)
                    return response.status_code == 200 and 'image' in response.headers['Content-Type']
                except requests.exceptions.RequestException:
                    return False

            embed_data = self.embeds.get(user_id)
            if not embed_data:
                return await ctx.respond("You don't have saved embeds!", ephemeral=True)
            options = [discord.SelectOption(label=f"Embed {i + 1}: {embed['title']}", value=str(i)) for i, embed in enumerate(embed_data)]
            select = discord.ui.Select(placeholder="Choose an embed you want to send!", options=options)
            async def select_callback(interaction: discord.Interaction):
                selected_index = int(select.values[0])
                selected_embed = embed_data[selected_index]
                embed = discord.Embed(
                    title=selected_embed["title"],
                    description=selected_embed["description"],
                    color=discord.Color.blue()

                )
                for field in selected_embed["fields"]:
                    embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

                if "author" in selected_embed:
                    embed.set_author(name=selected_embed["author"]["name"],
                                     icon_url=selected_embed["author"].get("icon_url", ""))

                if "image" in selected_embed:
                    image_url = selected_embed["image"]
                    if not is_valid_url(image_url):
                        return await interaction.response.send_message(
                            "The image path you provided doesn't seems to exist. Please try providing an existing one!",
                            ephemeral=True
                        )
                    embed.set_image(url=image_url)

                await interaction.channel.send(embed=embed)
                await interaction.response.send_message("Embed sent succesfully!", ephemeral=True)
            select.callback = select_callback
            await ctx.respond(view=discord.ui.View(select), ephemeral=True)

        elif action == "delete":
            self.embeds = self.load_embeds()
            embed_data = self.embeds.get(user_id)

            if not embed_data:
                return await ctx.respond("You don't have saved embeds!", ephemeral=True)

            options = [discord.SelectOption(label=f"Embed {i + 1}: {embed['title']}", value=str(i)) for i, embed in
                       enumerate(embed_data)]
            select = discord.ui.Select(placeholder="Choose an embed to delete!", options=options)

            async def select_callback(interaction: discord.Interaction):
                selected_index = int(select.values[0])

                modal = discord.ui.Modal(title="Confirm deletion")
                modal.add_item(discord.ui.InputText(label="Write YES to delete", required=True))

                async def modal_callback(interaction: discord.Interaction):
                    if modal.children[0].value.lower() == "igen":
                        del self.embeds[user_id][selected_index]
                        self.save_embeds()
                        await interaction.response.send_message("Embed succesfully deleted!", ephemeral=True)
                    else:
                        await interaction.response.send_message("Deletion aborted.", ephemeral=True)

                modal.callback = modal_callback
                await interaction.response.send_modal(modal)

            select.callback = select_callback
            await ctx.respond(view=discord.ui.View(select), ephemeral=True)


        elif action == "share":
            self.embeds = self.load_embeds()
            embed_data = self.embeds.get(user_id)
            if not embed_data:
                return await ctx.respond("You don't have any embeds to share!", ephemeral=True)

            embed_options = [
                discord.SelectOption(label=f"Embed {i + 1}: {embed['title']}", value=str(i))
                for i, embed in enumerate(embed_data)
            ]
            embed_select = discord.ui.Select(
                placeholder="Select the embed you want to share",
                options=embed_options
            )
            class EmbedSelectView(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.add_item(embed_select)
                    self.embed_select = embed_select

            async def embed_select_callback(interaction: discord.Interaction):
                if not embed_select.values:
                    return await interaction.response.send_message("You need to select an embed.", ephemeral=True)

                embed_index = int(embed_select.values[0])
                embed = embed_data[embed_index]
                await interaction.response.send_modal(UserIDModal(embed, ctx))

            embed_select.callback = embed_select_callback
            await ctx.respond(view=EmbedSelectView(), ephemeral=True)

    @embed_action.error
    async def embed_action_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            bugReport.sendReport("embedEditor", "embed_action", str(error))
            await ctx.respond("An error occurred while executeing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @editor.command(name="info", description="Information about the embed editor.")
    async def info(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Embed Editor",
            description="- This is an embed editor system that allows you to create, edit, send, delete and share embeds by using the /embed action command.\n- Remember that you can only create 5 embeds",
            color=discord.Color.blue()
        )
        embed.add_field(name="Features:", value="- **/embed action action: create** -  Start creating a new embed\n- **/embed action action: edit** - Edit one of your an existing embeds\n- **/embed action action: send** - Send one of you embeds to the channels which you are send the command in\n- **/embed action action: share** - Share one of your created embeds with other users of the bot\n- **/embed action action: delete** - Delete one of your embeds", inline=False)
        embed.set_footer(text="Use /embed action to get started!")
        await ctx.respond(embed=embed, ephemeral=True)

    @info.error
    async def info_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, discord.DiscordException):
            bugReport.sendReport("embedEditor", "info", str(error))
            await ctx.respond("An error occurred while executing command. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

class UserIDModal(discord.ui.Modal):
    def __init__(self, embed: discord.Embed, ctx: discord.ApplicationContext):
        super().__init__(title="Enter Target User ID")
        self.embed = embed
        self.ctx = ctx
        self.add_item(
            discord.ui.InputText(label="Target User ID", placeholder="Enter the user ID to share with"))

    async def callback(self, interaction: discord.Interaction):
        target_user_id = self.children[0].value
        try:
            target_user_id = int(target_user_id)
        except ValueError:
            return await interaction.response.send_message("Invalid user ID format. Please enter a valid ID.",
                                                           ephemeral=True)
        global target_user
        try:
            target_user = await self.ctx.guild.fetch_member(target_user_id)
        except discord.NotFound:
            return await interaction.response.send_message(
                "The user you wanted to share the embed with doesn't exist in this guild.", ephemeral=True)

        embed_obj = discord.Embed(
            title=self.embed["title"],
            description=self.embed["description"],
            color=discord.Color.blue()
        )
        for field in self.embed["fields"]:
            embed_obj.add_field(name=field["name"], value=field["value"], inline=False)
        if "image" in self.embed and self.embed["image"]:
            embed_obj.set_image(url=self.embed["image"])
        if "author" in self.embed and self.embed["author"]:
            author_data = self.embed["author"]
            author_name = author_data.get("name")
            author_icon = author_data.get("icon_url")

            if author_name:
                embed_obj.set_author(
                    name=author_name,
                    icon_url=author_icon if author_icon else discord.utils.MISSING
                )
        try:
            await target_user.send(
                embed=embed_obj,
                content=f"{self.ctx.user.name} has shared an embed with you! Do you want to accept it?",
                view=EmbedAcceptRejectView(self.embed, target_user.id, self.ctx.user.id)
            )
        except discord.Forbidden:
            await self.ctx.send(
                f"Unable to send a DM to <@{target_user.id}>. Please make sure your DMs are open.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"Embed has been shared with <@{target_user.id}> in the server!", ephemeral=True)


class EmbedAcceptRejectView(discord.ui.View):
    def __init__(self, embed: discord.Embed, target_user_id, sender_user_id):
        super().__init__()
        self.embed = embed
        self.target_user_id = target_user_id
        self.sender_user_id = sender_user_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("embeds.json", "r") as f:
            embeds = json.load(f)

        if str(self.target_user_id) not in embeds:
            embeds[str(self.target_user_id)] = []

        embeds[str(self.target_user_id)].append(self.embed)

        with open("embeds.json", "w") as f:
            json.dump(embeds, f, indent=4)

        try:
            await target_user.send("You have accepted the embed! It has been added to your collection.")

        except discord.Forbidden:

            await target_user.send("Unable to send a DM to you. Please make sure your DMs are open.")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await target_user.send("You have rejected the embed")
        sender = await interaction.client.fetch_user(self.sender_user_id)
        if sender:
            try:
                await sender.send(f"<@{self.target_user_id}> has rejected the embed you shared!")
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Unable to send a DM to the sender. They may have DMs disabled.", ephemeral=True)

        self.stop()


class EmbedEditView(discord.ui.View):
    def __init__(self, cog, user_id, embed_index):
        super().__init__()
        self.cog = cog
        self.user_id = str(user_id)
        self.embed_index = embed_index

    @discord.ui.select(placeholder="What do you want to edit?", options=[
        discord.SelectOption(label="Title change", value="title"),
        discord.SelectOption(label="Add/change description", value="description"),
        discord.SelectOption(label="Add field", value="field"),
        discord.SelectOption(label="Add author", value="author"),
        discord.SelectOption(label="Add image", value="image"),
        discord.SelectOption(label="Delete Title", value="titledelete"),
        discord.SelectOption(label="Delete Field", value="fielddelete"),
        discord.SelectOption(label="Delete Image", value="imagedelete"),
        discord.SelectOption(label="Delete Author", value="authordelete"),
        discord.SelectOption(label="Delete Description", value="descriptiondelete"),
    ])
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        embed_data = self.cog.embeds.get(self.user_id)[self.embed_index]
        if not embed_data:
            return await interaction.response.send_message("You don't have an active embed!", ephemeral=True)

        if select.values[0] == "title":
            modal = discord.ui.Modal(title="Change Title")
            modal.add_item(discord.ui.InputText(label="New title"))

            async def modal_callback(interaction: discord.Interaction):
                embed_data["title"] = modal.children[0].value
                self.cog.save_embeds()
                await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "description":
            modal = discord.ui.Modal(title="Add/change description")
            modal.add_item(discord.ui.InputText(label="New description"))

            async def modal_callback(interaction: discord.Interaction):
                embed_data["description"] = modal.children[0].value
                self.cog.save_embeds()
                await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "field":
            modal = discord.ui.Modal(title="Add Field")
            modal.add_item(discord.ui.InputText(label="Field name"))
            modal.add_item(discord.ui.InputText(label="Field value"))

            async def modal_callback(interaction: discord.Interaction):
                embed_data["fields"].append({"name": modal.children[0].value, "value": modal.children[1].value})
                self.cog.save_embeds()
                await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "author":
            modal = discord.ui.Modal(title="Add author")
            modal.add_item(discord.ui.InputText(label="Author name", required=True))
            modal.add_item(discord.ui.InputText(label="Author icon URL (optional)", required=False))

            async def modal_callback(interaction: discord.Interaction):
                author_name = modal.children[0].value
                author_icon = modal.children[1].value or None
                embed_data["author"] = {"name": author_name, "icon_url": author_icon}
                self.cog.save_embeds()
                await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "image":
            modal = discord.ui.Modal(title="Add image")
            modal.add_item(discord.ui.InputText(label="Image URL", required=True))

            async def modal_callback(interaction: discord.Interaction):
                embed_data["image"] = modal.children[0].value
                self.cog.save_embeds()
                await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "titledelete":
            modal = discord.ui.Modal(title="Do you want to delete the Title?")
            modal.add_item(discord.ui.InputText(label="Type YES if so", required=True))

            async def modal_callback(interaction):
                if(modal.children[0].value == "YES"):
                    del embed_data["title"]
                    self.cog.save_embeds()
                    await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "fielddelete":
            modal = discord.ui.Modal(title="Delete Field")
            modal.add_item(discord.ui.InputText(label="The index of the field you want to delete", required=True))
            async def modal_callback(interaction: discord.Interaction):
                try:
                    index = int(modal.children[0].value) - 1
                    if index < 0 or index >= len(embed_data["fields"]):
                        raise IndexError
                    del embed_data["fields"][index]
                    self.cog.save_embeds()
                    await self.update_embed(interaction, embed_data)
                    await interaction.followup.send("Field successfully deleted.", ephemeral=True)
                except (ValueError, IndexError):
                    await interaction.response.send_message("Invalid index provided.", ephemeral=True)
            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "imagedelete":
            modal = discord.ui.Modal(title="Do you want to delete the Image?")
            modal.add_item(discord.ui.InputText(label="Type YES if so", required=True))
            async def modal_callback(interaction: discord.Interaction):
                if (modal.children[0].value == "YES"):
                    del embed_data["image"]
                    self.cog.save_embeds()
                    await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "authordelete":
            modal = discord.ui.Modal(title="Do you want to delete the Author")
            modal.add_item(discord.ui.InputText(label="Type YES if so", required=True))

            async def modal_callback(interaction: discord.Interaction):
                if (modal.children[0].value == "YES"):

                    embed_data["author"] = {"name": "", "icon_url": ""}
                    self.cog.save_embeds()
                    await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        elif select.values[0] == "descriptiondelete":
            modal = discord.ui.Modal(title="Do you want to delete the Description")
            modal.add_item(discord.ui.InputText(label="Type YES if so", required=True))

            async def modal_callback(interaction: discord.Interaction):
                if (modal.children[0].value == "YES"):
                    del embed_data["description"]
                    self.cog.save_embeds()
                    await self.update_embed(interaction, embed_data)

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

    async def update_embed(self, interaction: discord.Interaction, embed_data):
        embed = discord.Embed(
            title=embed_data["title"],
            description=embed_data["description"],
            color=discord.Color.blue()
        )

        for field in embed_data["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        if "author" in embed_data:
            embed.set_author(name=embed_data["author"]["name"], icon_url=embed_data["author"].get("icon_url", ""))
        if "image" in embed_data:
            embed.set_image(url=embed_data["image"])
        await interaction.response.edit_message(embed=embed, view=self)


def setup(bot: discord.Bot):
    bot.add_cog(EmbedEditor(bot))