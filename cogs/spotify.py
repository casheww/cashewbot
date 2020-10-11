import discord
from discord.ext import commands
import json
import aiohttp
import re

# another yoinked code structure (dont blame me)

# uhhhhh get your api from https://developer.spotify.com
with open('_keys.json') as f:
    # this was literally the only way it would grab 2 api keys and i dont know why aaaaaaaa
    shit = json.load(f)
    spot_id = shit['spotify_id']
    spot_sec = shit['spotify_sec']


class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='''Grabs details on an artist or track and embeds them nicely.'
                                  Use is: `##spotifygrab <artist,track or both delimited by comma> query`  ''',
                      aliases=['spotify'])
    async def spotifygrab(self, ctx, reqtype, query):

        # lets actually check the input given is correct shall we

        template = ['artist', 'track']
        outcomes = []

        reqtype = reqtype.split(",")
        # if the input given is akin to a list chances are its going to be artist,track so do that
        if len(reqtype) < 2:
            # assume that the user has entered only one parameter
            # use regex to make sure the exact word is given
            for word in template:
                for otherword in reqtype:
                    # this magical voodoo checks that the start and end of the string only
                    # contain the word and nothing else
                    if re.search(r'^' + word + r'$', otherword):
                        # this needs one outcome passed (True) to continue
                        outcomes.append(True)
                    else:
                        outcomes.append(False)

            if outcomes.count(True) == 1:
                pass
            else:
                # user is fucking stupid, exit
                await ctx.send("Parameters given are incorrect! Check help for more info.")
                return

        elif len(reqtype) == 2:
            # assume that the user has actually bothered to look at the help on how to use it
            # and has entered a comma delimited list (kind of)
            # same re search just thiccer

            for word in template:
                for otherword in reqtype:
                    if re.search(r'^' + word + r'$', otherword):
                        # this needs two outcomes passed (True) to continue
                        outcomes.append(True)
                    else:
                        outcomes.append(False)

            if outcomes.count(True) == 2:
                pass

            else:
                await ctx.send("Parameters given are incorrect! Check help for more info.")
                return
        else:
            # the user has entered more than 2 parameters (dumb fuck), exit
            await ctx.send("Parameters given are incorrect!")
            return

        # join reqtype back at the end
        reqtype = ','.join(reqtype)

        # uhhh i didn't anticipate the user to delimit with a space but fuck it
        # they'll get some wacky search results

        # authentication section (grabbing a token per request probably isn't good)
        # but fuck it i'm allowed

        data = {'grant_type': 'client_credentials'}
        async with self.bot.web.post(url="https://accounts.spotify.com/api/token", data=data,
                                     auth=aiohttp.BasicAuth(login=spot_id, password=spot_sec)) as r:
            resp = await r.json()

            token = resp['access_token']
        # the bread and butter of my code
        # (idk this is barebones kind of probably add it to it later)
        headers = {"Authorization": "Bearer %s" % token}

        # right listen this was the only way that worked with requests so im keeping it
        async with self.bot.web.get("https://api.spotify.com/v1/search?q=" + query + "&type=" + reqtype, headers=headers) as r:
            res = await r.json()

        # if it wasn't we probably wouldn't be here but oh well
        if 'artist' in reqtype:
            try:
                artist = res['artists']['items'][0]
            except KeyError:
                print("idk something fucked up here")
                return

            e = discord.Embed(title="Top Result for Artist", colour=discord.Colour.green())
            e.set_thumbnail(url=artist['images'][2]['url'])
            e.add_field(name="Artist Name:", value=artist['name'])
            e.add_field(name="Artist's Page:", value=artist['external_urls']['spotify'])
            e.add_field(name="Followers:", value=artist['followers']['total'])
            e.add_field(name="Genres:", value=artist['genres'][0]+","+artist['genres'][1])
            e.set_footer(text="API Request Made: " + res['artists']['href'])
            await ctx.send(embed=e)

        if 'track' in reqtype:
            try:
                tracks = res['tracks']['items'][0]
            except KeyError:
                print("idk something fucked up here")
                return

            e = discord.Embed(title="Top Result For Tracks", colour = discord.Colour.green())
            e.set_thumbnail(url=tracks['album']['images'][2]['url'])
            e.add_field(name="Track Name:", value=tracks['name'])
            e.add_field(name="Track: ", value=tracks['external_urls']['spotify'])
            e.add_field(name="Track on Spotify: ", value=tracks['external_urls']['spotify'])
            try:
                e.add_field(name="Artists: ", value=tracks['artists'][0]['name']+","+tracks['artists'][1]['name']+","+tracks['artists'][2]['name'])
            except IndexError:
                e.add_field(name="Artists: ", value=tracks['artists'][0]['name'])

            e.add_field(name="Release Date", value=tracks['album']['release_date'])
            e.set_footer(text="API Request Made: " + res['tracks']['href'])
            await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Spotify(bot))
