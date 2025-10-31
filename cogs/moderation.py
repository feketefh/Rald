import discord
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
from discord import option

import datetime

from modules.bugReport import bugReport
from modules import subCommands

class admin(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    admin_group = subCommands.admin_group

    @admin_group.command(name="ban", description="Ban a user")
    @option("member", discord.Member, description="Which user do you want to ban?", required=True)
    @option("reason", str, description="Reason for ban", required=False)
    @has_permissions(ban_members=True)
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str):
        if member == ctx.author:
            await ctx.respond("You cannot ban yourself.")
            return
        await member.ban(reason=reason)
        await ctx.respond(f'{member} has been banned.')
    
    @ban.error
    async def ban_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to ban members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to ban members.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "ban", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @admin_group.command(name="hackban", description="Ban a user using ID")
    @option("member_id", int, description="ID of the user to ban", required=True)
    @option("reason", str, description="Reason for ban", required=False)
    @has_permissions(ban_members=True)
    async def hackban(self, ctx: discord.ApplicationContext, member_id: int, reason: str):
        member: discord.Member = self.bot.get_user(member_id)
        if member:
            await member.ban(reason=reason)
            await ctx.respond(f'{member} has been banned.')
        else:
            await ctx.respond("User not found.")
    
    @hackban.error
    async def hackban_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to ban members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to ban members.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "hackban", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @admin_group.command(name="unban", description="Unban a user")
    @option("member_id", int, description="ID of the user to unban", required=True)
    @has_permissions(ban_members=True)
    async def unban(self, ctx : discord.ApplicationContext, member_id: int):
        member = discord.utils.get(ctx.guild.bans(), id=member_id)
        if member:
            await ctx.guild.unban(member)
            await ctx.respond(f'{member} has been unbanned.')
        else:
            await ctx.respond("User not found.")
    
    @unban.error
    async def unban_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to unban members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to unban members.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "unban", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @admin_group.command(name="kick", description="Kick a user")
    @option("member", discord.Member, description="Which user do you want to kick?", required=True)
    @option("reason", str, description="Reason for kick", required=False)
    @has_permissions(kick_members=True)
    async def kick(self, ctx : discord.ApplicationContext, member: discord.Member, reason: str):
        await member.kick(reason=reason)
        await ctx.respond(f'{member} has been kicked.')
    
    @kick.error
    async def kick_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to kick members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to kick members.", ephemeral=True)
        else:
            await ctx.respond(f"An error occurred while attempting to kick the user: {error}", ephemeral=True)

    @admin_group.command(name="tempmute", description="Mute a user")
    @option("member", discord.Member, description="Which user do you want to mute?", required=True)
    @option("duration", str, description="The duration of the mute", required=True)
    @option("reason", str, description="Reason for mute", required=False)
    @has_permissions(mute_members=True)
    async def mute(self, ctx : discord.ApplicationContext, member: discord.Member, duration_str: str, reason: str):

        duration_map = {"m": 1, "h": 60, "d": 1440}
        duration_total = 0

        for unit in duration_str:
            if unit.isdigit():
                duration_value = int(unit)
            else:
                duration_value = 1
            if unit.lower() in duration_map:
                duration_total += duration_value * duration_map[unit.lower()]

        duration = datetime.timedelta(minutes=duration_total)
        await member.timeout_for(duration, reason=reason)
        await ctx.respond(f'{member} has been muted for {duration_str}.')
    
    @mute.error
    async def mute_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to mute members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to mute members.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "mute", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @admin_group.command(name="unmute", description="Unmute a user")
    @option("member", discord.Member, description="Which user do you want to unmute?", required=True)
    @has_permissions(mute_members=True)
    async def unmute(self, ctx : discord.ApplicationContext, member: discord.Member):
        if not member.timed_out():
            await ctx.respond(f'{member} is not muted.')
            return
        await member.remove_timeout()
        await ctx.respond(f'{member} has been unmuted.')
    
    @unmute.error
    async def unmute_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to unmute members.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to unmute members.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "unmute", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @admin_group.command(name="purge", description="Delete the given amount of messages")
    @option("amount", int, description="The amount of messages to delete", required=True)
    @has_permissions(manage_messages=True)
    async def purge(self, ctx: discord.ApplicationContext, amount: int):
        msgCount = await ctx.channel.purge(limit=amount)
        delMsgCount = len(msgCount)
        embed = discord.Embed(title=f"Purge - {amount} messages", description=" ", color=discord.Color.green())
        embed.add_field(name="Succesfuly deleted:", value=amount, inline=False)
        embed.add_field(name="Failed to delete:", value=amount - delMsgCount, inline=False)
        await ctx.respond(embed=embed, delete_after=5)
    @purge.error
    async def purge_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to delete messages.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to delete messages.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "purge", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    
    @admin_group.command(name="lock", description="Lock a channel")
    @option("channel", discord.TextChannel, description="Channel to lock", required=False)
    @has_permissions(manage_channels=True)
    async def lock(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        if channel:
            await channel.edit(reason="Channel locked", permission_overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
            await ctx.respond(f'Channel {channel.mention} has been locked.')
        else:
            await ctx.channel.edit(reason="Channel locked", permission_overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
    
    @lock.error
    async def lock_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to lock channels.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to lock channels.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "lock", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
    
    @admin_group.command(name="unlock", description="Unlock a channel")
    @option("channel", discord.TextChannel, description="Channel to unlock", required=False)
    @has_permissions(manage_channels=True)
    async def unlock(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        if channel:
            await channel.edit(reason="Channel unlocked", permission_overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=True)})
            await ctx.respond(f'Channel {channel.mention} has been unlocked.')
        else:
            await ctx.channel.edit(reason="Channel unlocked", permission_overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=True)})
    
    @unlock.error
    async def unlock_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to unlock channels.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to unlock channels.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "unlock", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)


    @admin_group.command(name="nuke", description="Nuke a channel")
    @option("channel", discord.TextChannel, description="Channel to nuke", required=False)
    @has_permissions(manage_channels=True)
    async def nuke(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        if channel:
            new_channel = await channel.clone(reason="Nuked")

            await channel.delete(reason="Nuked")

            embed = discord.Embed(title="This channel has been nuked", description=" ", color=discord.Color.orange())
            embed.set_image(url="https://c.tenor.com/h9eFBIbNv4cAAAAC/tenor.gif")
            await ctx.respond(f"Channel has been nuked \n- New cannel: {new_channel.mention} \n- New channel ID: {new_channel.id}", ephemeral=True)
            await new_channel.send(embed=embed)
        else:
            current_channel = ctx.channel
            new_channel = await current_channel.clone(reason="Nuked")

            await current_channel.delete(reason="Nuked")

            embed = discord.Embed(title="This channel has been nuked", description=" ", color=discord.Color.orange())
            embed.set_image(url="https://c.tenor.com/h9eFBIbNv4cAAAAC/tenor.gif")
            await new_channel.send(embed=embed)

    @nuke.error
    async def nuke_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.Forbidden):
            await ctx.respond("I do not have permission to nuke channels.")
        elif isinstance(error, MissingPermissions):
            await ctx.respond("You do not have the necessary permissions to nuke channels.", ephemeral=True)
        else:
            bugReport.sendReport("admin", "nuke", str(error))
            await ctx.respond("An error occurred while sending the bug report. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(admin(bot))