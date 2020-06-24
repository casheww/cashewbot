import discord
from discord.ext import commands
from assets import anglen
import botdb, json
import aiohttp


with open('_keys.gitignore') as file:
    keys = json.load(file)
    yandex_key = keys['yandex']

y_link = "https://translate.yandex.net/api/v1.5/tr.json/translate"


async def to_target_lang(text: str, target_language: str):
    aiohttp_session = aiohttp.ClientSession()

    params = {'key': yandex_key, 'text': text, 'lang': target_language}
    async with aiohttp_session.post(url=y_link, params=params) as r:
        j = await r.json()

    try:
        final_text = j['text'][0]
        translate_info = j['lang']

        await aiohttp_session.close()
        return [final_text, translate_info]

    except KeyError:
        await aiohttp_session.close()
        return ['error']


class Translate(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Translates text to English.")
    async def en(self, ctx, *, text):
        data = await to_target_lang(text, "en")
        if data[0] != "error":
            await ctx.send(f"*{ctx.author.name} --- {data[1]}* :\n{data[0]}")
        else:
            await ctx.send("Invalid language code")


    @commands.command(description="Translates text to a target language.")
    async def translate(self, ctx, target_language: str, *, text):
        data = await to_target_lang(text, target_language)
        if data[0] != "error":
            await ctx.send(f"*{ctx.author.name} --- {data[1]}* :\n{data[0]}")
        else:
            await ctx.send("Invalid language code")


    @commands.command(description="Use in a channel to take in messages in another language to be translated. "
                                  "Translations to the target language are output to the out_channel. "
                                  "Compatible langs: "
                                  "https://tech.yandex.com/translate/doc/dg/concepts/api-overview-docpage/#api-overview__languages . "
                                  "Requires 'Manage Server'.")
    @commands.has_permissions(manage_guild=True)
    async def toggle_lang_tunnel(self, ctx, out_channel: discord.TextChannel = None, target_language: str = 'en'):
        guild_info = await botdb.get_guild_data(self.client.db, ctx.guild.id)

        if 'lang' in guild_info.keys()\
                and 'in' in guild_info['lang'].keys()\
                and ctx.channel.id == guild_info['lang']['in']:
            del guild_info['lang']
            await ctx.send('Translation logging now **disabled** for this channel.')

        else:
            if out_channel is None:
                await ctx.send(
                    f'An out_channel must be defined to enable this feature. E.g.: toggle_lang_tunnel {ctx.channel.mention} en')
                return

            guild_info['lang'] = {'in': ctx.channel.id, 'out': out_channel.id, 'outlang': target_language}

            await ctx.send('Translation logging now **enabled** for this channel (input).')
            await out_channel.send('Translation logging now **enabled** for this channel (output).')

        info = json.dumps(guild_info)

        await botdb.dump_guild_data(self.client.db, ctx.guild.id, info)


    @commands.Cog.listener()
    async def on_message(self, message):

        guild_info = await botdb.get_guild_data(self.client.db, message.guild.id)

        if not guild_info:
            return
        if 'lang' not in guild_info.keys():
            return

        if 'in' in guild_info['lang'].keys() and message.channel.id == guild_info['lang']['in']:

            data = await to_target_lang(text=message.content, target_language=guild_info['lang']['outlang'])

            if data[0] != 'error' and data[1][:2] != data[1][3:]:  # en-en or fr-fr -e.g.- won't be logged
                out = self.client.get_channel(guild_info['lang']['out'])
                await out.send(f'-----\n*{message.author} --- {data[1]}* :\n{data[0]}')


    @commands.command(description="Encrypt text using the Anglen substitution cipher, "
                                  "devised by DGTILL.")
    async def toanglen(self, ctx, *, text):
        await ctx.send(anglen.eta(text))


    @commands.command(description="Decrypt text from Anglen.")
    async def fromanglen(self, ctx, *, text):
        await ctx.send(anglen.ate(text))


def setup(client):
    client.add_cog(Translate(client))
