import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import option

from typing import Union
from PIL import Image
from io import BytesIO
import requests
from modules.bugReport import bugReport

class image(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.http_status_codes = [
            "100", "101", "102", "103", "200", "201", "202", "203", "204", "205", "206", "207", "208", "214", "226",
            "300", "301", "302", "303", "304", "305", "307", "308", "400", "401", "402", "403", "404", "405", "406",
            "407", "408", "409", "410", "411", "412", "413", "414", "415", "416", "417", "418", "419", "420", "421",
            "422", "423", "424", "425", "426", "428", "429", "431", "444", "450", "451", "495", "496", "497", "498",
            "499", "500", "501", "502", "503", "504", "506", "507", "508", "509", "510", "511", "521", "522", "523",
            "525", "530", "599"
        ]

    image = discord.SlashCommandGroup("image", "Image generator")

    @image.command(name="httpcat", description="Get an HTTP status code cat image")
    @option("code", description="HTTP status code", required=True)
    async def httpcat(self, ctx: discord.ApplicationContext, code: str):
        if code not in self.http_status_codes:
            return await ctx.respond("Invalid HTTP status code. Please provide a valid one.")
        r = requests.get(f"https://http.cat/{code}")
        embed = discord.Embed(title="HTTP Cat", color=discord.Colour.blue())
        embed.set_image(url=r.url)
        await ctx.respond(embed=embed)

    @httpcat.error
    async def httpcat_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("image", "httpcat", str(error))
            await ctx.respond("An error occurred while sending the HTTP cat image. Automatic bug report has been successfully sent to the developers.", ephemeral=True)


    @image.command(name="rimage", description="Get a random image")
    async def rimage(self, ctx: discord.ApplicationContext):
        r = requests.get("https://picsum.photos/300/300")

        embed = discord.Embed(title="Image", color=discord.Colour.blue())
        embed.set_image(url=r.url)
        await ctx.respond(embed=embed)
    
    @rimage.error
    async def rimage_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("image", "rimage", str(error))
            await ctx.respond("An error occurred while sending the random image. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @image.command(name="rdog", description="Get a random dog image")
    async def rdog(self, ctx: discord.ApplicationContext):
        r = requests.get("https://dog.ceo/api/breeds/image/random")

        embed = discord.Embed(title="Dog", color=discord.Colour.blue())
        embed.set_image(url=r.json()["message"])
        await ctx.respond(embed=embed)

    @rdog.error
    async def rdog_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("image", "rdog", str(error))
            await ctx.respond("An error occurred while sending the dog image. Automatic bug report has been successfully sent to the developers.", ephemeral=True)
    
    @image.command(name="rcat", description="Get a random cat image")
    async def rcat(self, ctx: discord.ApplicationContext):
        r = requests.get("https://api.thecatapi.com/v1/images/search")

        embed = discord.Embed(title="Cat", color=discord.Colour.blue())
        embed.set_image(url=r.json()[0]["url"])
        await ctx.respond(embed=embed)

    @rcat.error
    async def rcat_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("image", "rcat", str(error))
            await ctx.respond("An error occurred while sending the cat image. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

    @image.command(name="overlay", description="Add an overlay to a user's avatar!")
    @option("user", Union[discord.User], description="Select a user")
    @option("overlay", description="Choose an overlay", choices=["Comrade", "Pride", "Glass", "Jail", "Passed", "Triggered", "GTA IV Wasted"])
    async def image_overlay(self, ctx: discord.ApplicationContext, user: Union[discord.User], overlay: str):
        if not user.avatar == None:
            if overlay == "GTA IV Wasted":
                overlay = "wasted"
            api = f"https://some-random-api.com/canvas/overlay/{overlay}"
            r = requests.get(api, params={"avatar": user.avatar.url})
            embed = discord.Embed(title=f"{overlay} {user.name}", color=discord.Colour.blue())
            embed.set_image(url=r.url)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("User has no avatar.")

    @image_overlay.error
    async def image_overlay_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            bugReport.sendReport("image", "image_overlay", str(error))
            await ctx.respond("An error occurred while trying to overlay the image. Automatic bug report has been successfully sent to the developers.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(image(bot))