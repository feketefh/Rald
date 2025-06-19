from discord.ext import commands
from discord import option
import discord
from typing import Union

from modules.bugReport import bugReport

class utils(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    utils = discord.SlashCommandGroup("utils", "Utility commands")

    @utils.command(name="userinfo", description="Get every information about a user")
    @option("member", Union[discord.Member], description="Which user's info do you want?", required=False)
    async def userinfo(self, ctx: discord.ApplicationContext, member: discord.Member):
        if not member:
            member = ctx.author
            embed = discord.Embed(title=f"{member}'s info", description=f"ID: {member.id}", color=discord.Colour.random())
            embed.add_field(name="Nickname:", value=member.nick if member.nick else "No nickname", inline=False)
            embed.add_field(name="Bot:", value="Yes" if member.bot else "No", inline=False)
            embed.add_field(name="Created at:", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Joined at:", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Roles:", value=', '.join([role.name for role in member.roles]), inline=False)
            embed.add_field(name="Status:", value=member.status, inline=False)
            embed.add_field(name="Activity:", value=member.activity.name if member.activity else "No activity", inline=False)
            embed.add_field(name="Top role:", value=member.top_role.name, inline=False)
            embed.set_thumbnail(url=member.avatar)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title=f"{member}'s info", description=f"ID: {member.id}", color=discord.Colour.random())
            embed.add_field(name="Nickname:", value=member.nick if member.nick else "No nickname", inline=False)
            embed.add_field(name="Bot:", value="Yes" if member.bot else "No", inline=False)
            embed.add_field(name="Created at:", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Joined at:", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Roles:", value=', '.join([role.name for role in member.roles]), inline=False)
            embed.add_field(name="Status:", value=member.status, inline=False)
            embed.add_field(name="Activity:", value=member.activity.name if member.activity else "No activity", inline=False)
            embed.add_field(name="Top role:", value=member.top_role.name, inline=False)
            embed.set_thumbnail(url=member.avatar)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.respond(embed=embed)
    
    @userinfo.error
    async def userinfo_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("utils", "userinfo", str(error))
            await ctx.respond("An error occurred while getting user information. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @utils.command(name="serverinfo", description="Get every information about the server")
    async def serverinfo(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title=ctx.author.guild.name, description=f"ID: {ctx.author.guild.id}", color=discord.Colour.green())
        embed.add_field(name="Owner:", value=f"<@{ctx.author.guild.owner_id}>", inline=False)
        embed.add_field(name="Creation Date:", value=ctx.author.guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Roles:", value=len(ctx.author.guild.roles), inline=False)

        vanity_url = getattr(ctx.author.guild, "vanity_url", None)
        embed.add_field(name="Vanity URL:", value=vanity_url if vanity_url else "None", inline=False)

        embed.add_field(name="Text Channels:", value=len(ctx.author.guild.text_channels), inline=False)
        embed.add_field(name="Voice Channels:", value=len(ctx.author.guild.voice_channels), inline=False)
        embed.add_field(name="Categories:", value=len(ctx.author.guild.categories), inline=False)
        embed.add_field(name="Verification Level:", value=ctx.author.guild.verification_level, inline=False)
        #embed.add_field(name="MFA:", value="Enabled" if ctx.author.guild.mfa_level == discord.GuildMfaLevel.Elevated else "Disabled", inline=False)

        if ctx.author.guild.banner:
            embed.set_image(url=ctx.author.guild.banner)
        if ctx.author.guild.icon:
            embed.set_thumbnail(url=ctx.author.guild.icon)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

        await ctx.respond(embed=embed)

    @serverinfo.error
    async def serverinfo_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("utils", "serverinfo", str(error))
            await ctx.respond("An error occurred while getting server information. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @utils.command(name="avatar", description="Get the avatar of a user")
    @option("member", Union[discord.Member], description="Which user's avatar do you want?", required=False)
    async def avatar(self, ctx: discord.ApplicationContext, member: discord.Member):
        if not member:
            member = ctx.author
            embed = discord.Embed(title=f"{member}'s avatar", color=discord.Colour.random())
            embed.set_image(url=member.avatar)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title=f"{member}'s avatar", color=discord.Colour.random())
            embed.set_image(url=member.avatar)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.respond(embed=embed)
    
    @avatar.error
    async def avatar_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("utils", "avatar", str(error))
            await ctx.respond("An error occurred while getting the avatar. Automatic bug report has been successfully sent to the developers.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(utils(bot))