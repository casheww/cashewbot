import discord
from discord.ext import commands
import db_interface
import json


with open('_keys.json') as file:
    keys = json.load(file)
    yandex_key = keys['yandex']

y_link = "https://translate.yandex.net/api/v1.5/tr.json/translate"


class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def to_target_lang(self, text: str, target_language: str):
        aiohttp_session = self.bot.web

        params = {'key': yandex_key, 'text': text, 'lang': target_language}
        async with aiohttp_session.post(url=y_link, params=params) as r:
            j = await r.json()

        try:
            final_text = j['text'][0]
            translate_info = j['lang']

            return [final_text, translate_info]

        except KeyError:
            return ['error']

    @commands.command(description="Translates text to English.")
    async def en(self, ctx, *, text):
        data = await self.to_target_lang(text, "en")
        if data[0] != "error":
            await ctx.send(f"*{ctx.author.name} --- {data[1]}* :\n{data[0]}")
        else:
            await ctx.send("Invalid language code")

    @commands.command(description="Translates text to a target language.")
    async def translate(self, ctx, target_language: str, *, text):
        data = await self.to_target_lang(text, target_language)
        if data[0] != "error":
            await ctx.send(f"*{ctx.author.name} --- {data[1]}* :\n{data[0]}")
        else:
            await ctx.send("Invalid language code")

    @commands.command(
        description="Use in a channel to take in messages in another language to be translated. "
        "Translations to the target language are output to the out_channel. "
        "Compatible langs: "
        "https://tech.yandex.com/translate/doc/dg/concepts/api-overview-docpage/#api-overview__languages .",
        brief="Manage Server permission Required.")
    @commands.has_guild_permissions(manage_guild=True)
    async def toggle_lang_tunnel(self, ctx, out_channel: discord.TextChannel = None, target_language: str = 'en'):
        guild_info = await db_interface.get_guild_data(self.bot.db, ctx.guild.id)

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

            guild_info['lang'] = {
                'in': ctx.channel.id,
                'out': out_channel.id,
                'outlang': target_language}

            await ctx.send('Translation logging now **enabled** for this channel (input).')
            await out_channel.send('Translation logging now **enabled** for this channel (output).')

        info = json.dumps(guild_info)

        await db_interface.dump_guild_data(self.bot.db, ctx.guild.id, info)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.id == self.bot.user.id:
            return

        guild_info = await db_interface.get_guild_data(self.bot.db, message.guild.id)

        if not guild_info:
            return
        if 'lang' not in guild_info.keys():
            return

        if 'in' in guild_info['lang'].keys(
        ) and message.channel.id == guild_info['lang']['in']:

            data = await self.to_target_lang(text=message.content, target_language=guild_info['lang']['outlang'])

            # en-en or fr-fr -e.g.- won't be logged
            if data[0] != 'error' and data[1][:2] != data[1][3:]:
                out = self.bot.get_channel(guild_info['lang']['out'])
                await out.send(f'-----\n*{message.author} --- {data[1]}* :\n{data[0]}')


def setup(bot):
    bot.add_cog(Translate(bot))
