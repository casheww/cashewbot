import discord
from discord.ext import commands
import json, botdb
from datetime import datetime as dt


async def cash_setup(db, guild):
    info = json.dumps({'info': {'name': guild.name, 'join': str(dt.now().strftime(f'%d/%m/%Y'))}})
    await botdb.dump_guild_data(db, guild.id, info)


class ServerTools(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Resets ALL the data stored about the guild. "
                                  "Use with caution. Requires 'Administrator'.")
    @commands.has_guild_permissions(administrator=True)
    async def reset_guild_data(self, ctx):
        await cash_setup(self.client.db, ctx.guild)
        await ctx.send('Guild data has been reset.')


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        w_embed = discord.Embed(title='CashewBot is in!', colour=discord.Colour.blue())
        w_embed.set_author(name=guild.name, icon_url=guild.icon_url)
        w_embed.add_field(name='Setup Tips',
                          value="1 > The 'help' command will come in handy! Default command prefix: ]\n"
                                "2 > Check out the 'toggle_modlog' command to keep track of mod actions.\n"
                                "3 > Enable status updates with 'toggle_cash_shout'.\n"
                                "4 > Keep it chill!\n"
                                "5 > Want a fresh start with me? Try the 'reset_guild_data' command.")
        if guild.system_channel:
            await guild.system_channel.send(embed=w_embed)
        else:
            await guild.text_channels[0].send(embed=w_embed)

        await cash_setup(self.client.db, guild)


def setup(client):
    client.add_cog(ServerTools(client))
