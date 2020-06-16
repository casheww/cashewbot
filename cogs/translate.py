from discord.ext import commands
from assets import anglen


class Translate(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Encrypt text using the Anglen substitution cipher, "
                                  "devised by DGTILL.")
    async def toanglen(self, ctx, *, text):
        await ctx.send(anglen.eta(text))


    @commands.command(description="Decrypt text from Anglen.")
    async def fromanglen(self, ctx, *, text):
        await ctx.send(anglen.ate(text))


def setup(client):
    client.add_cog(Translate(client))
