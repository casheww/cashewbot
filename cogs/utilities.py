from datetime import datetime as dt
import discord
from discord.ext import commands
import platform


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Returns the uptime of the bot.")
    async def uptime(self, ctx):
        time = dt.now() - self.bot.start_time
        await ctx.send(time)

    @commands.command(description="Returns the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.command(description="Returns bot info.")
    async def info(self, ctx):

        embed = discord.Embed(
            description=self.bot.description,
            colour=ctx.colour)
        embed.set_author(name=str(self.bot.user),
                         url="https://github.com/casheww/cashewbot")
        embed.add_field(name="Commands", value=str(len(self.bot.commands)))
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)))
        embed.add_field(name="CashewBot Guild",
                        value=f"[Join here]({self.bot.support_invite})")
        embed.add_field(
            name="\u200B",
            value=f"**CashewBot**: {self.bot.version}\n"
            f"**Python**: {platform.python_version()} | "
            f"**discord.py**: {discord.__version__}",
            inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="Returns the bot invite link.")
    async def invite(self, ctx):
        await ctx.send(f"<{self.bot.invite}>")


def setup(bot):
    bot.add_cog(Utilities(bot))
