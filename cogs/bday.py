import discord
from discord.ext import commands
import db_interface, json
import datetime as dt


class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(description="Group containing bday commands.",
                    brief="Subcommands can only be used in servers")
    @commands.guild_only()
    async def bday(self, ctx):
        ...


    @bday.before_invoke
    async def before_bday(self, ctx):
        if ctx.message.content.strip(ctx.prefix) != "bday toggle":

            data = await db_interface.get_bdays(ctx.bot.db, ctx.guild.id)

            if isinstance(data, type(None)):
                return await ctx.send("Birthday functionality is disabled in this server.")


    @bday.command(description="Toggle birthday functionality in this server. "
                              "Off by default.",
                  brief="Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def toggle(self, ctx):
        base_data = await db_interface.get_bdays(self.bot.db, ctx.guild.id)

        if not isinstance(base_data, type(None)):
            await db_interface.delete_bdays(self.bot.db, ctx.guild.id)
            return await ctx.send("Birthday functionality for this guild has been "
                                  "**disabled**, and all bday data has been deleted.")

        data = json.dumps({})
        await db_interface.dump_bdays(self.bot.db, ctx.guild.id, data)
        await ctx.send("Birthday functionality for this guild has been **enabled**!")


    @bday.command(description="Register your birthday to the server bday list. "
                              "Date format: DD/MM.")
    async def set(self, ctx, date):
        data = await db_interface.get_bdays(self.bot.db, ctx.guild.id)

        try:
            date_obj = dt.datetime.strptime(date, "%d/%m")
        except ValueError:
            return await ctx.send("Please use the date format: DD/MM. E.g.: 18/06.")

        data[str(ctx.author.id)] = int(date_obj.strftime("%j"))
        await db_interface.dump_bdays(self.bot.db, ctx.guild.id, json.dumps(data))
        await ctx.send(f"Your birthday has been set to {date}! :tada:")


    @bday.command(description="Removes your birthday from the server's bday list.")
    async def remove(self, ctx):
        data = await db_interface.get_bdays(self.bot.db, ctx.guild.id)

        try:
            del data[str(ctx.author.id)]
            await ctx.send("Successfully deleted your birthday. Have fun not aging, dumbass.")
        except KeyError:
            await ctx.send("Nothing to delete.")

        await db_interface.dump_bdays(self.bot.db, ctx.guild.id, json.dumps(data))


    @bday.command(description="Returns a list of all birthdays registered in the guild "
                              "over the next week.",
                  aliases=["soon"])
    async def upcoming(self, ctx):
        data = await db_interface.get_bdays(self.bot.db, ctx.guild.id)
        start = int(dt.datetime.today().strftime("%j"))-1
        end = start + 7

        embed = discord.Embed(colour=discord.Colour.red(),
                              title=f"Upcoming birthdays! :tada:")
        embed.set_author(name=ctx.guild.name)

        any_found = False
        rel_data = {}

        if end > 365:
            end -= 365

            for i in data:
                b_int = data[i]

                if b_int <= end or start <= b_int:
                    rel_data[i] = b_int
                    any_found = True

        else:
            for i in data:
                b_int = data[i]

                if start <= b_int <= end:
                    rel_data[i] = b_int
                    any_found = True

        if not any_found:
            embed.add_field(name="\u200B", value="No birthdays in the next week :(")

        else:
            sorted_data = sorted(rel_data, key=rel_data.get)

            for i in sorted_data:
                member = ctx.guild.get_member(int(i)).mention
                b_str = dt.datetime.strptime(str(data[i]), "%j").strftime("%d %B")
                embed.add_field(name="\u200B", value=f"{member}  ||  **{b_str}**")

        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Birthdays(bot))
