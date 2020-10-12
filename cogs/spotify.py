import discord
from discord.ext import commands
import json
import aiohttp
import re

# another yoinked code structure (dont blame me)

# uhhhhh get your api from https://developer.spotify.com
with open('_keys.json') as f:
    # this was literally the only way it would grab 2 api keys and i dont know
    # why aaaaaaaa
    shit = json.load(f)
    spot_id = shit['spotify_id']
    spot_sec = shit['spotify_sec']
    spot_refresh_token = shit['spotify_refresh_token']


class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_client_auth(self):
        # authentication section (grabbing a token per request probably isn't good)
        # but fuck it i'm allowed

        data = {'grant_type': 'client_credentials'}
        async with self.bot.web.post(url="https://accounts.spotify.com/api/token", data=data,
                                     auth=aiohttp.BasicAuth(login=spot_id, password=spot_sec)) as r:
            resp = await r.json()

            token = resp['access_token']
        # the bread and butter of my code
        # (idk this is barebones kind of probably add it to it later)
        return {"Authorization": "Bearer %s" % token}

    async def fetch_auth_flow(self):
        # https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
        # this is step 3 or something. the rest of the code is only necessary once to get up to here.
        data = {
            "grant_type": "refresh_token",
            "refresh_token": spot_refresh_token
        }

        async with self.bot.web.post(url="https://accounts.spotify.com/api/token", data=data,
                                     auth=aiohttp.BasicAuth(login=spot_id, password=spot_sec)) as r:
            resp = await r.json()
        return resp["access_token"]

    @commands.command(
        description='''Grabs details on an artist or track and embeds them nicely.'
                                  Use is: `##spotifygrab <artist,track or both delimited by comma> query`  ''',
        aliases=['spotify'])
    async def spotifygrab(self, ctx, reqtype, *, query):

        # lets actually check the input given is correct shall we

        template = ['artist', 'track']
        outcomes = []

        reqtype = reqtype.split(",")
        # if the input given is akin to a list chances are its going to be
        # artist,track so do that
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

        headers = await self.fetch_client_auth()

        # right listen this was the only way that worked with requests so im
        # keeping it
        async with self.bot.web.get("https://api.spotify.com/v1/search?q=" + query + "&type=" + reqtype, headers=headers) as r:
            res = await r.json()

        # if it wasn't we probably wouldn't be here but oh well
        if 'artist' in reqtype:
            try:
                artist = res['artists']['items'][0]
            except (KeyError, IndexError):
                print("idk something fucked up here")

            else:
                e = discord.Embed(
                    title="Top Result for Artist",
                    colour=discord.Colour.green())
                e.set_thumbnail(url=artist['images'][2]['url'])
                e.add_field(name="Artist Name:", value=artist['name'])
                e.add_field(
                    name="Info:",
                    value=f"[Artist's page]({artist['external_urls']['spotify']})\n"
                    f"Followers: {artist['followers']['total']}")

                if artist['genres']:
                    e.add_field(name="Genres:",
                                value=", ".join(artist['genres'][:2]))

                await ctx.send(embed=e)

        if 'track' in reqtype:
            try:
                tracks = res['tracks']['items'][0]
            except (KeyError, IndexError):
                print("idk something fucked up here")
                return

            else:
                e = discord.Embed(
                    title="Top Result For Tracks",
                    colour=discord.Colour.green())
                e.set_thumbnail(url=tracks['album']['images'][2]['url'])
                e.add_field(name="Track Name:", value=tracks['name'])
                e.add_field(
                    name="Track:",
                    value=f"[Click me!]({tracks['external_urls']['spotify']})")

                try:
                    e.add_field(
                        name="Artists: ",
                        value=tracks['artists'][0]['name'] +
                        "," +
                        tracks['artists'][1]['name'] +
                        "," +
                        tracks['artists'][2]['name'])
                except IndexError:
                    e.add_field(
                        name="Artists:", value=", ".join(
                            a['name'] for a in tracks['artists']))

                e.add_field(
                    name="Release Date",
                    value=tracks['album']['release_date'])
                await ctx.send(embed=e)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sp_collate(self, ctx, playlist_id, limit: int = 100):
        if limit == 0:
            limit = None

        tracks = []
        async for m in ctx.channel.history(limit=limit):
            if m.content.startswith("https://open.spotify.com/track/"):
                print("a")
                track_uri = (m.content.split("/")[-1]).split("?")[0]
                tracks.append(track_uri)

                if len(tracks) > 100:
                    break

        headers = {
            "Authorization": f"Bearer {await self.fetch_auth_flow()}",
            "Content-Type": "application/json"
        }
        data = {"uris": [f"spotify:track:{u}" for u in tracks]}

        async with self.bot.web.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers,
                                     json=data) as r:
            res = await r.json()
            print(res)

        await ctx.send(f"{len(tracks)} added to playlist @ {playlist_id}")


def setup(bot):
    bot.add_cog(Spotify(bot))
