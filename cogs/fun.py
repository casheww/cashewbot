import discord
from discord.ext import commands
from custom_checks import *


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(hidden=True)
    @is_celery()
    async def vore(self, ctx, member: discord.Member):
        await ctx.send(f"{member.mention} was vored by {ctx.author.name}.")


    @vore.error
    async def vore_eh(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("you are not worthy")


def setup(client):
        client.add_cog(Fun(client))
