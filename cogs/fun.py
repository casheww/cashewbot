import discord
from discord.ext import commands
import custom_checks


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client


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


def setup(client):
        client.add_cog(Fun(client))
