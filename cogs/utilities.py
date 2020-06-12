from discord.ext import commands
from datetime import datetime as dt


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Returns the uptime of the bot.")
    async def uptime(self, ctx):
        time = dt.now() - self.client.start_time
        await ctx.send(time)


    @commands.command(description="Returns the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"Ping: `{round(self.client.latency*1000)}ms`")


    @commands.command(description="Returns a list of all of the loaded cogs.")
    async def cogs(self, ctx):
        outstr = ""
        for cog in self.client.cogs:
            outstr += f"{cog}, "
        await ctx.send(f"**Loaded cogs:**\n{outstr[:-2]}")


def setup(client):
    client.add_cog(Utilities(client))
