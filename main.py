import aiohttp
import aiosqlite
from cogs.count import CountingChannel
from datetime import datetime
import db_interface
from discord.ext import commands
import jishaku
import json
import os
from src.context import CustomContext


class CashewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix,
                         case_insensitive=True,
                         description="A generic Discord bot... Written by casheww in Python.")

        self.db = None
        self.counting_channels = []
        self.invite = "https://discord.com/api/oauth2/authorize?client_id=706534185992454198" \
                      "&permissions=67628112&scope=bot"
        self.log_id = 584971929778257930
        self.prefix_dict = {}
        self.start_time = None
        self.support_invite = "https://discord.gg/qK5JkSG"
        self.version = "4.2.0"
        self.web = None


    async def get_prefix(self, message):
        default_prefix = "##"

        if message.guild:
            try:
                return self.prefix_dict[message.guild.id]
            except (KeyError, TypeError):
                pass

        return default_prefix


    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)


    @staticmethod
    def format_counting_data(data):
        formatted = []
        for g in data:
            fib = True if g[5] == 1 else False
            formatted.append(CountingChannel(g[1], g[0], g[2], g[3], g[4], fib))
        return formatted


    def get_counting_channel(self, **kwargs):
        try:
            if "channel_id" in kwargs:
                return [c for c in self.counting_channels if c.id == kwargs["channel_id"]][0]
            elif "guild_id" in kwargs:
                return [c for c in self.counting_channels if c.guild_id == kwargs["guild_id"]][0]
        except IndexError:
            return None


    async def on_message(self, message):
        if self.get_counting_channel(channel_id=message.channel.id) and \
                not message.content.endswith("toggle_count") and \
                not message.author.guild_permissions.manage_channels:
            return

        await self.process_commands(message)



    async def startup(self):
        await self.wait_until_ready()

        log_ch = self.get_channel(self.log_id)
        await log_ch.send("bot started")

        self.db = await aiosqlite.connect("db/bot.db")

        self.counting_channels = self.format_counting_data(await db_interface.get_all_count_data(self.db))
        self.start_time = datetime.now()
        self.web = aiohttp.ClientSession()


        data = await db_interface.get_all_guilds(self.db)
        for entry in data:
            try:
                prefix = json.loads(entry[1])["info"]["prefix"]
                self.prefix_dict[entry[0]] = prefix
            except KeyError:
                pass

        print(f"===== bot started =====\n"
              f"\tlogged in as:\t{self.user}\n"
              f"\tid:\t\t{self.user.id}\n"
              f"\tdt:\t\t{self.start_time}\n\n")


if __name__ == "__main__":
    with open("_keys.json") as f:
        token = json.load(f)["discord"]

    bot = CashewBot()
    bot.loop.create_task(bot.startup())

    bot.load_extension("jishaku")
    for ext in os.listdir("cogs"):
        if ext.endswith(".py"):
            bot.load_extension(f"cogs.{ext[:-3]}")

    bot.run(token)
