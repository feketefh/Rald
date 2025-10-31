import discord
from discord.ext import commands
from discord import option

import requests
import random
import urllib.parse
from typing import Union

from modules.bugReport import bugReport
from modules import subCommands

class fun(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    fun = subCommands.fun

    @fun.command(name="rquote", description="Get a random quote")
    async def rquote(self, ctx: discord.ApplicationContext):
        r = requests.get("https://zenquotes.io/api/quotes/")
        embed = discord.Embed(title="Quote", color=discord.Colour.blue())
        embed.add_field(name="Author:", value=r.json()[0]["q"], inline=False)
        embed.add_field(name="Quote:", value=r.json()[0]["a"], inline=False)
        await ctx.respond(embed=embed)

    @rquote.error
    async def rquote_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "rquote", str(error))
            await ctx.respond("An error occurred while sending the quote. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
        

    @fun.command(name="rjoke", description="Get a random joke")
    async def rjoke(self, ctx: discord.ApplicationContext):
        r = requests.get("https://official-joke-api.appspot.com/random_joke")
        embed = discord.Embed(title="Joke", color=discord.Colour.blue())
        embed.add_field(name="Setup:", value=r.json()["setup"], inline=False)
        embed.add_field(name="Punchline:", value=r.json()["punchline"], inline=False)
        await ctx.respond(embed=embed)
    
    @rjoke.error
    async def rjoke_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "rjoke", str(error))
            await ctx.respond("An error occurred while sending the joke. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @fun.command(name="rinsult", description="Get a random insult")
    async def rinsult(self, ctx: discord.ApplicationContext):
        r = requests.get("https://insult.mattbas.org/api/insult.json")
        embed = discord.Embed(title="Insult", color=discord.Colour.blue())
        embed.add_field(name="Insult:", value=r.json()["insult"], inline=False)
        await ctx.respond(embed=embed)
    
    @rinsult.error
    async def rinsult_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "rinsult", str(error))
            await ctx.respond("An error occurred while sending the insult. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
            
    @fun.command(name="8ball", description="Ask the magic 8 ball a question")
    @option("question", str, description="Your question")
    async def eightball(self, ctx: discord.ApplicationContext, question: str):
        responses = [
            "Yes",
            "No",
            "Maybe",
            "Ask again later",
            "Definitely",
            "Absolutely not",
            "I don't know",
            "Of course",
            "Not a chance",
        ]
        response = random.choice(responses)
        embed = discord.Embed(title="Magic 8 Ball", color=discord.Colour.blue())
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=response, inline=False)
        await ctx.respond(embed=embed)
    
    @eightball.error
    async def eightball_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "8ball", str(error))
            await ctx.respond("An error occurred while sending the 8ball response. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @fun.command(name="iq", description="IQ test")
    @option("user", Union[discord.User], description="User to test")
    async def iq_test(self, ctx: discord.ApplicationContext, user: discord.User):
        if user is None:
            user = ctx.author
        iq = random.randint(1, 200)
        embed = discord.Embed(title="IQ Test", color=discord.Colour.blue())
        embed.add_field(name=f"{user.name}'s IQ:", value=f"{iq}", inline=False)
        await ctx.respond(embed=embed)
    
    @iq_test.error
    async def iq_test_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "iq", str(error))
            await ctx.respond("An error occurred while sending the IQ test. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)

    @fun.command(name="coinflip", description="Flip a coin")
    @option("choice", str, description="Heads or Tails", choices=["Heads", "Tails"])
    async def coinflip(self, ctx: discord.ApplicationContext, choice: str):
        result = random.choice(["Heads", "Tails"])
        if result == choice:
            result = f"{result} - You win!"
            color = discord.Colour.green()
        else:
            result = f"{result} - You lose!"
            color = discord.Colour.red()
        embed = discord.Embed(title="Coin Flip", color=color)
        embed.add_field(name="Your choice:", value=choice, inline=False)
        embed.add_field(name="Result:", value=result, inline=False)
        await ctx.respond(embed=embed)

    @coinflip.error
    async def coinflip_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "coinflip", str(error))
            await ctx.respond("An error occurred while sending the coin flip result. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
    
    @fun.command(name="rolldice", description="Roll a dice")
    async def rolldice(self, ctx: discord.ApplicationContext):
        dice_roll = random.randint(1, 6)
        embed = discord.Embed(title="Dice Roll", color=discord.Colour.blue())
        embed.add_field(name="Result:", value=f"You rolled a {dice_roll}", inline=False)
        await ctx.respond(embed=embed)
    
    @rolldice.error
    async def rolldice_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "rolldice", str(error))
            await ctx.respond("An error occurred while sending the dice roll result. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)
    
    @fun.command(name="lmgtfy", description="Let Me Google That For You")
    @option("query", str, description="The query you want to search for")
    async def lmgify(self, ctx: discord.ApplicationContext, query: str):
        query = query.strip()
        if not query:
            await ctx.respond("Query cannot be empty.", ephemeral=True)
            return
        base_url = "https://letmegooglethat.com/?q="
        encoded_query = urllib.parse.quote_plus(query)
        await ctx.respond(f"{base_url + encoded_query}")
    
    
    @lmgify.error
    async def lmgify_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("fun", "lmgtfy", str(error))
            await ctx.respond("An error occurred while sending the LMGTFY link. Automatic bug report has been succesfully sent to the developers.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(fun(bot))