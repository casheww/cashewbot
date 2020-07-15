from discord.ext import commands
import json, botdb, aiosqlite
from datetime import datetime as dt
import aiohttp


# - - - - - -
#   CASHEWBOT V4  ---  PHOENIX PROJECT
#       Another write-over inspired by the
#       rapid and wonderful new development of
#       Discord bot 'Geo', produced by DGTILL.
#
#       Uh oh, Natasha's bot is also getting
#       a reboot. This is a bot war. I'm doomed.
#
#       OH, Tom's also doing it now fdkjfkjsfldjkl
#
#       Please don't mind my inconsistent styling.
#       I know there are conflicting "" and '',
#       I'm just way too lazy to change it all to
#       double quotes.
#
#       Sole developer:
#           Github  : https://github.com/casheww
#           Discord : @casheww#7881 [444857307843657739]
#
#           https://tse3.mm.bing.net/th?id=OIP.pr73nqt5kalqmB2ykQPmKwAAAA&pid=Api
# - - - - - -


with open('_keys.gitignore') as file:
    keys = json.load(file)
    bot_token = keys['discord']


async def get_prefix(clnt, message):
    default_prefix = '##'

    if message.guild:
        guild_info = await botdb.get_guild_data(clnt.db, message.guild.id)
        try:
            return guild_info['info']['prefix']
        except (KeyError, TypeError):
            pass

    return default_prefix


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

@client.event
async def on_ready():
    """
    The lack of the bot var 'db' is an indication that this is the start of the uptime.
    That's important to check for because on_ready can fire more than once during the uptime.
    The use of 'db' as a bot var prevents multiple concurrent db connections.
    """

    if not hasattr(client, 'db'):
        client.db = await aiosqlite.connect('db/cashewbot.db')
        client.start_time = dt.now()
        client.web = aiohttp.ClientSession()
        client.uno_guilds = await get_uno_guilds(client.db)

    out = '========== READY ==========\n' \
        f'\tNAME :\t\t{str(client.user)}\n' \
        f'\tID :\t\t{client.user.id}\n' \
        f'\tDT :\t\t{dt.now()}\n' \
        '========== READY ==========\n'
    print(out)


@client.command()
@commands.is_owner()
async def load(ctx, ext_name):
    client.load_extension(f"cogs.{ext_name}")

    await ctx.message.add_reaction('\U00002705')
    with open('log.txt', 'a+') as f:
        f.write(f'--- Loaded {ext_name}\n')


@client.command()
@commands.is_owner()
async def reload(ctx, ext_name):
    client.reload_extension(f"cogs.{ext_name}")

    await ctx.message.add_reaction('\U00002705')
    with open('log.txt', 'a+') as f:
        f.write(f'--- Loaded {ext_name}\n')


@client.command()
@commands.is_owner()
async def unload(ctx, ext_name):
    client.unload_extension(f"cogs.{ext_name}")

    await ctx.message.add_reaction('\U00002705')
    with open('log.txt', 'a+') as f:
        f.write(f'--- Loaded {ext_name}\n')


extensions = ['announce',
              'bday',
              'devtools',
              'eh',
              'fun',
              'help',
              'nasa',
              'servertools',
              'stat_handler',
              'translate',
              'utilities',
              'uno',
              'weather']
for extension in extensions:
    try:
        client.load_extension(f'cogs.{extension}')
    except Exception as e:
        exc = f"{type(extension).__name__}: {e}"
        print(f"Failed to load extension {extension}\n{e}")


async def get_uno_guilds(db):
    async with db.cursor() as c:
        data = await c.execute("SELECT * FROM guilds")
        data = await data.fetchall()

    uno_guilds = {}         # list of guilds in which uno is enabled

    for guild in data:
        guild_dict = json.loads(guild[1])
        if 'uno' in guild_dict.keys():
            uno_guilds[guild[0]] = guild_dict['uno']

    return uno_guilds


client.run(bot_token)
