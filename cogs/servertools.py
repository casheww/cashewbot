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


    @commands.command(description="Resets ALL the data stored by the bot about the guild. "
                                  "Use with caution.",
                      brief="Administrator permission required.")
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


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await botdb.delete_guild(self.client.db, guild.id)
        await botdb.delete_announce(self.client.db, guild.id)


    @commands.command(description="Returns stats and info regarding the current server.",
                      aliases=['guildinfo', 'guild_info'],
                      brief="Server-only command.")
    @commands.guild_only()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        e = discord.Embed(title=guild.name, colour=guild.me.color)
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Owner", value=guild.owner.mention)
        e.add_field(name="Region", value=guild.region)
        e.add_field(name="Member count", value=f"{guild.member_count}")
        e.add_field(name="Server boosts", value=f"{guild.premium_subscription_count}")
        e.add_field(name="Creation date", value=f"{guild.created_at.strftime('%d/%m/%Y')}")

        saved_data = await botdb.get_guild_data(self.client.db, guild.id)
        print(saved_data['info']['join'])
        e.add_field(name="My join date", value=saved_data['info']['join'])

        await ctx.send(embed=e)


    @commands.command(description="Set a custom command prefix for this guild.",
                      aliases=['setprefix'],
                      brief="Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, prefix: str = ""):
        if prefix == "":
            await ctx.send("Please enter a custom command prefix. E.g.: `setprefix !`")
        else:
            guild_info = await botdb.get_guild_data(self.client.db, ctx.guild.id)

            guild_info['info']['prefix'] = prefix
            info = json.dumps(guild_info)

            await botdb.dump_guild_data(self.client.db, ctx.guild.id, info)

            await ctx.send(f"Prefix set to: `{prefix}`")



def setup(client):
    client.add_cog(ServerTools(client))
