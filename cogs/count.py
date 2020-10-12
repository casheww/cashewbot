import db_interface
from discord.ext import commands, tasks


class CountingChannel:
    def __init__(
            self,
            my_id,
            guild_id,
            last_member_id,
            number0,
            number1,
            fibonacci):
        self.id = my_id
        self.guild_id = guild_id
        self.last_member_id = last_member_id
        self.num0 = number0
        self.num1 = number1
        self.fibonacci = fibonacci


class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.count_backup.start()

    async def cog_unload(self):
        self.count_backup.stop()

    @staticmethod
    def msg_int_check(message):
        int(message.content)
        return True

    @commands.command(
        description="Toggle counting on/off for the current channel.",
        brief="Manage Channels permission required.")
    @commands.has_guild_permissions(manage_channels=True)
    async def toggle_count(self, ctx):
        counting_channel = self.bot.get_counting_channel(guild_id=ctx.guild.id)

        if counting_channel is not None:
            self.bot.counting_channels.remove(counting_channel)
            await self.bot.get_channel(counting_channel.id).send("Counting stopped.")

            if ctx.channel.id == counting_channel.id:
                return

        await ctx.send("Do you want to do Fibonacci counting? (Enter `no` for no. Anything else will be a yes.)")
        fibonacci_msg = await self.bot.wait_for("message", timeout=20)
        if fibonacci_msg.content.lower() == "no":

            await ctx.send("Pick a starting number.")
            start_num = int((await self.bot.wait_for("message", check=self.msg_int_check, timeout=20)).content)

            self.bot.counting_channels.append(
                CountingChannel(
                    ctx.channel.id,
                    ctx.guild.id,
                    self.bot.user.id,
                    start_num,
                    1,
                    False))

            await ctx.send(f"**Let the counting begin!**\n{start_num}")

        else:

            self.bot.counting_channels.append(CountingChannel(
                ctx.channel.id, ctx.guild.id, self.bot.user.id, 1, 1, True
            ))

            await ctx.send("**Let the counting begin!**\n1\n1")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        count_ch = self.bot.get_counting_channel(channel_id=message.channel.id)
        if not count_ch:
            return

        if message.author.id == count_ch.last_member_id:
            return await message.delete()

        content = message.content.split()[0]
        target = count_ch.num0 + count_ch.num1

        if content != str(target):
            return await message.delete()

        i = self.bot.counting_channels.index(count_ch)
        self.bot.counting_channels[i].last_member_id = message.author.id
        if count_ch.fibonacci:
            self.bot.counting_channels[i].num1 = count_ch.num0
            self.bot.counting_channels[i].num0 = int(content)

        else:
            self.bot.counting_channels[i].num1 = 1
            self.bot.counting_channels[i].num0 = int(content)

    @tasks.loop(minutes=3)
    async def count_backup(self):
        for c in self.bot.counting_channels:
            await db_interface.dump_count_data(self.bot.db, c.guild_id, c.id, c.last_member_id,
                                               c.num0, c.num1, c.fibonacci)

    @commands.command(
        description="Returns the last recorded count for this guild.")
    @commands.guild_only()
    async def last_count(self, ctx):
        data = self.bot.get_counting_channel(guild_id=ctx.guild.id)
        last_member = ctx.guild.get_member(data.last_member_id)
        await ctx.send(f"Last number: `{data.num0}`\nLast member: `{last_member}`\nChannel: <#{data.id}>")


def setup(bot):
    bot.add_cog(Counting(bot))
