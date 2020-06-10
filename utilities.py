from discord.ext import commands
from datetime import datetime as dt


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def uptime(self, ctx):
        """
        Returns the uptime of the bot.
        """
        time = dt.now() - self.client.start_time
        await ctx.send(time)


    @commands.command()
    async def ping(self, ctx):
        """
        Returns the latency of the bot.
        """
        await ctx.send(f"Ping: `{round(self.client.latency*1000)}ms`")



def setup(client):
    client.add_cog(Utilities(client))
