import discord
from discord.ext import commands
from datetime import datetime as dt
import json


with open('_keys.gitignore') as f:
    nasa_key = json.load(f)['nasa']


class NASA(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Returns NASA's Astronomy Picture of the Day for today"
                                  "or a given date. Date format: YYYY-MM-DD")
    async def apod(self, ctx, *image_date):
        if image_date:
            try:
                date_obj = dt.strptime(image_date[0], '%Y-%m-%d')
                date_str = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                await ctx.send('Please use date format: YYYY-MM-DD')
                return
        else:
            date_str = dt.today().strftime('%Y-%m-%d')


        p = {"date": date_str, "hd": 'True', 'api_key': nasa_key}

        async with self.client.web.get(url=f"https://api.nasa.gov/planetary/apod", params=p) as r:
            j = await r.json()

        try:
            if j['media_type'] == 'video':
                e = discord.Embed(title="NASA - Astronomy Picture of the Day",
                                  colour=discord.Colour.dark_purple(),
                                  description=f"{j['explanation'].split('.')[0]}.")
                e.add_field(name="Today's picture is a video...", value=f"[Click Me]({j['url']})")

            else:
                e = discord.Embed(title="NASA - Astronomy Picture of the Day",
                                  colour=discord.Colour.dark_purple(),
                                  description=f"{j['explanation'].split('.')[0]}.")
                e.add_field(name=j['date'], value=j['title'])
                e.set_image(url=j['hdurl'])
        except KeyError:
            await ctx.send("Sorry, that date is out of the accepted range.")
            return

        await ctx.send(embed=e)

def setup(client):
    client.add_cog(NASA(client))
