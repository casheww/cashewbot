import discord
from discord.ext import commands
import json, db_interface
from datetime import datetime as dt
from main import CashewBot


async def cash_setup(db, guild):
    info = json.dumps({'info': {'name': guild.name, 'join': str(dt.now().strftime(f'%d/%m/%Y'))}})
    await db_interface.dump_guild_data(db, guild.id, info)


class ServerTools(commands.Cog):
    def __init__(self, bot: CashewBot):
        self.bot = bot


    @staticmethod
    def w_embed(guild):
        w_embed = discord.Embed(title='CashewBot is here!', colour=discord.Colour.blue())
        w_embed.set_author(name=guild.name, icon_url=guild.icon_url)
        w_embed.add_field(name='Setup Tips',
                          value="1 > The `help` command will come in handy! Default command prefix: ##\n"
                                "2 > Keep it chill!\n"
                                "3 > Want a fresh start with me? Try the 'reset_guild_data' command.\n"
                                "4 > @ me in a message to see this embed again.")

        return w_embed


    @commands.command(description="Resets ALL the data stored by the bot about the guild. "
                                  "Use with caution.",
                      brief="Administrator permission required.")
    @commands.has_guild_permissions(administrator=True)
    async def reset_guild_data(self, ctx):
        await cash_setup(self.bot.db, ctx.guild)
        await ctx.send('Guild data has been reset.')


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            w = self.w_embed(guild)

            def check(ctx):
                return ctx.guild.id == guild.id

            c = await self.bot.wait_for("command", check=check)
            await c.send(embed=w)

        except:
            pass
        await cash_setup(self.bot.db, guild)


    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            w = self.w_embed(message.guild)
            await message.channel.send(embed=w)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await db_interface.delete_guild(self.bot.db, guild.id)


    @commands.command(description="Returns stats and info regarding the current server.",
                      aliases=['serverinfo', 'guild_info'],
                      brief="Server-only command.")
    @commands.guild_only()
    async def server_info(self, ctx):
        guild = ctx.guild
        e = discord.Embed(title=guild.name, colour=guild.me.color)
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Owner", value=guild.owner.mention)
        e.add_field(name="Region", value=guild.region)
        e.add_field(name="Member count", value=f"{guild.member_count}")
        e.add_field(name="Server boosts", value=f"{guild.premium_subscription_count}")
        e.add_field(name="Creation date", value=f"{guild.created_at.strftime('%d/%m/%Y')}")

        saved_data = await db_interface.get_guild_data(self.bot.db, guild.id)
        print(saved_data['info']['join'])
        e.add_field(name="My join date", value=saved_data['info']['join'])

        await ctx.send(embed=e)


    @commands.command(description="Set a custom command prefix for this guild. "
                                  "To add trailing whitespace, enter the new prefix "
                                  "as in-line code, e.g. \\`prefix \\`",
                      brief="Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, prefix: str = ""):
        if prefix == "" or len(prefix) > 10:
            return await ctx.send("Please enter a custom command prefix. E.g.: `set_prefix \\`!\\``. "
                           "Prefix must be less than 10 characters long.")

        prefix = prefix.strip("`")

        guild_info = await db_interface.get_guild_data(self.bot.db, ctx.guild.id)
        guild_info['info']['prefix'] = prefix
        await db_interface.dump_guild_data(self.bot.db, ctx.guild.id, guild_info)
        self.bot.prefix_dict[ctx.guild.id] = prefix

        await ctx.send(f"Prefix set to: `{prefix}`")



def setup(bot):
    bot.add_cog(ServerTools(bot))
