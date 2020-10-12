import discord
from discord.ext import commands
import json


# yoinked half of this code from nasa.py (no regrets)

# api key used is from https://openweathermap.org
with open('_keys.json') as f:
    weather_key = json.load(f)['weather']


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description='Returns weather information based on city given.',
        aliases=['getweather'])
    async def get_weather(self, ctx, weather_city):
        # fuck out of here with those imperial measurements :flag_gb:
        headers = {'q': weather_city, 'units': 'metric', 'appid': weather_key}

        async with self.bot.web.get(url=f'https://api.openweathermap.org/data/2.5/weather', params=headers) as req:
            res = await req.json()

        e = discord.Embed(title='OpenWeatherMap - Current Weather Data',
                          colour=discord.Colour.teal(),
                          # this whole line just looks terrible
                          description=('Current Temperature for {}: ' + str(res['main']['temp']) + '°C').format(weather_city.title()))

        e.add_field(
            name='Feels Like Temperature',
            value=str(
                res['main']['feels_like']) +
            '°C',
            inline=True)
        e.add_field(
            name='Min Temperature Today',
            value=str(
                res['main']['temp_min']) +
            '°C',
            inline=True)
        e.add_field(
            name='Max Temperature Today',
            value=str(
                res['main']['temp_max']) +
            '°C',
            inline=True)
        e.add_field(
            name='Atmospheric Pressure',
            value=str(
                res['main']['pressure']) +
            ' hPa',
            inline=True)
        e.add_field(
            name='Humidity',
            value=str(
                res['main']['humidity']) +
            '%',
            inline=True)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Weather(bot))
