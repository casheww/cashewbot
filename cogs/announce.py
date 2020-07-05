import discord
from discord.ext import commands
import botdb
from custom_checks import *


class Announcements(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Toggle CashewBot progress and status announcements in "
                                  "the current channel.",
                      brief="Administrator permission required.")
    @commands.has_guild_permissions(administrator=True)
    async def toggle_announce(self, ctx):
        announce_data = await botdb.get_announce(self.client.db, ctx.guild.id)

        # no current announcement data set for guild
        if not announce_data:
            wh = await ctx.channel.create_webhook(name="CashewBot Announcements")

            await botdb.dump_announce(self.client.db, ctx.guild.id, wh.url, wh.id)
            await ctx.send("CashewBot Announcements are now **enabled** in this channel!")

        else:
            old_wh = await self.client.fetch_webhook(announce_data[2])
            await old_wh.delete()

            # set for the current guild & already enabled in the current channel
            if old_wh.channel == ctx.channel:
                await botdb.delete_announce(self.client.db, ctx.guild.id)
                await ctx.send("CashewBot Announcements are now **disabled** in this channel.")

            # set for the current guild but enabled in a different channel
            else:
                wh = await ctx.channel.create_webhook(name="CashewBot Announcements")

                await botdb.dump_announce(self.client.db, ctx.guild.id, wh.url, wh.id)
                await ctx.send("CashewBot Announcements for this guild have been moved to this channel.")


    @commands.command(hidden=True)
    @commands.check_any(commands.is_owner(), is_celery())
    async def cash_shout(self, ctx, *, message):
        announce_data = await botdb.get_all_announce(self.client.db)

        with open("db/announce_count.txt", "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))

        embed = discord.Embed(colour=discord.Colour.from_rgb(147, 204, 203))
        embed.set_author(name=f"<auth: {ctx.author.name}>", icon_url=ctx.author.avatar_url)
        embed.add_field(name=f"№ {count}", value=message)

        for wh_tuple in announce_data:
            wh = await self.client.fetch_webhook(wh_tuple[2])

            await wh.send(embed=embed, avatar_url=self.client.user.avatar_url)

        await ctx.message.add_reaction('\U00002705')



def setup(client):
    client.add_cog(Announcements(client))
