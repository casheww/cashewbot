import base64
import discord
from discord.ext import commands
import custom_checks
import io
from main import CashewBot
from PIL import Image
import random
from socket import timeout as MCTimeout
from src import minecraft as mc, avg_image_colour


class Fun(commands.Cog):
    def __init__(self, bot: CashewBot):
        self.bot = bot


    @commands.command(hidden=True)
    @custom_checks.is_celery()
    async def vore(self, ctx, member: discord.Member):
        await ctx.send(f"{member.mention} was vored by {ctx.author.name}.")


    @vore.error
    async def vore_eh(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("you are not worthy")


    @commands.command(hidden=True)
    async def casheww(self, ctx):
        await ctx.send("stupid stupid stupid")


    @commands.command(description="Generates a random keysmash.",
                      aliases=["ks"])
    async def keysmash(self, ctx):
        letters = ["s", "d", "f", "j", "k"]
        keysmash = ""

        for i in range(0, random.randint(8, 14)):
            keysmash += random.choice(letters)

        await ctx.send(keysmash)


    @commands.command(description="Gets some stats from a Minecraft server.",
                    aliases=["mc"])
    async def minecraft(self, ctx, ip, port="25565"):
        try:
            data, icon_data = await self.bot.loop.run_in_executor(None, mc.server_info, ip, port)
        except MCTimeout:
            return await ctx.send("Server connection timed out.")

        img_data = base64.b64decode(icon_data[22:])
        img = Image.open(io.BytesIO(img_data))

        rgb = avg_image_colour.average(img)
        rgb = [int(x) for x in rgb]

        buffer = io.BytesIO()
        img.save(buffer, "png")
        buffer.seek(0)
        file = discord.File(buffer, filename="image.png")

        e = discord.Embed.from_dict(data)
        e.colour = discord.Colour.from_rgb(*rgb)
        e.set_thumbnail(url="attachment://image.png")

        await ctx.send(embed=e, file=file)



def setup(bot):
    bot.add_cog(Fun(bot))
