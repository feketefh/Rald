import discord
from discord.ext import commands
from discord import option

import random

from modules.bugReport import bugReport
from modules import subCommands

class number(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    number = subCommands.number

    @number.command(name="random", description="Generates a random number between two given numbers")
    @option("min_val", int, description="Lower limit", required=True)
    @option("max_val", int, description="Upper limit", required=True)
    async def random_number(self, ctx: discord.ApplicationContext, min_val: int, max_val: int):
        num = random.randint(min_val, max_val)
        embed = discord.Embed(title=f"Random Number: {num}", description=f"Min value: {min_val}\nMax value: {max_val}", color=discord.Colour.random())
        await ctx.respond(embed=embed)
    
    @random_number.error
    async def random_number_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, TypeError):
            await ctx.respond("Both min_val and max_val must be numbers.")
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("number", "random_number", str(error))
            await ctx.respond("An error occurred while generating the random number. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @number.command(name="addition", description="Adds two given numbers together")
    @option("num1", int, description="First number", required=True)
    @option("num2", int, description="Second number", required=True)
    async def addition(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 + num2
        embed = discord.Embed(title=f"Addition: {result}", description=f"Number 1: {num1}\nNumber 2: {num2}", color=discord.Colour.random())
        await ctx.respond(embed=embed)
    
    @addition.error
    async def addition_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, TypeError):
            await ctx.respond("Both num1 and num2 must be numbers.")
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("number", "addition", str(error))
            await ctx.respond("An error occurred while performing the addition. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @number.command(name="subtraction", description="Subtract two numbers from each other")
    @option("num1", int, description="First number", required=True)
    @option("num2", int, description="Second number", required=True)
    async def subtraction(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 - num2
        embed = discord.Embed(title=f"Subtraction: {result}", description=f"Number 1: {num1}\nNumber 2: {num2}", color=discord.Colour.random())
        await ctx.respond(embed=embed)

    @subtraction.error
    async def subtraction_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, TypeError):
            await ctx.respond("Both num1 and num2 must be numbers.")
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("number", "subtraction", str(error))
            await ctx.respond("An error occurred while performing the subtraction. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @number.command(name="multiplication", description="Multiplies two numbers together")
    @option("num1", int, description="First number", required=True)
    @option("num2", int, description="Second number", required=True)
    async def multiplication(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 * num2
        embed = discord.Embed(title=f"Multiplication: {result}", description=f"Number 1: {num1}\nNumber 2: {num2}", color=discord.Colour.random())
        await ctx.respond(embed=embed)
    
    @multiplication.error
    async def multiplication_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, TypeError):
            await ctx.respond("Both num1 and num2 must be numbers.")
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("number", "multiplication", str(error))
            await ctx.respond("An error occurred while performing the multiplication. Automatic bug report has been successfully sent to the developers.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(number(bot))