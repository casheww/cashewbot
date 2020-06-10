import discord
from discord.ext import commands
from main import get_prefix


def command_plural(count):
    if count == 1:
        return 'command'
    else:
        return 'commands'


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="Returns a helpful message!")
    async def help(self, ctx, help_call=None):
        embed = discord.Embed(colour=ctx.author.colour)
        icon_url = self.client.user.avatar_url

        if not help_call:
            outstr = ""
            for cog in self.client.cogs:
                cog_commands = self.client.cogs[cog].get_commands()

                command_count = len(cog_commands)
                for c in cog_commands:
                    if c.hidden:
                        command_count -= 1

                if command_count >= 1:
                    outstr += f"**{cog}** - {command_count} {command_plural(command_count)}\n"

            embed.set_author(name="CashewBot - Help", icon_url=icon_url)
            embed.add_field(name="Command Groups", value=outstr)
            embed.set_footer(text="Try `help group-name`!")
            await ctx.send(embed=embed)
            return

        for cog in self.client.cogs:
            if help_call.title() == cog:
                cog_commands = self.client.cogs[cog].get_commands()
                outstr = ""

                for c in cog_commands:
                    if not c.hidden:
                        outstr += f"**{c.qualified_name}** - {c.description}\n\n"

                embed.set_author(name=f"CashewBot - {cog} Group", icon_url=icon_url)
                embed.add_field(name="Commands", value=outstr)
                embed.set_footer(text="Try `help command-name`!")
                await ctx.send(embed=embed)
                return

        for command in self.client.commands:
            if help_call == command.qualified_name or help_call in command.aliases:
                if not command.hidden:
                    embed.set_author(name=f"CashewBot - {command.qualified_name} Command", icon_url=icon_url)
                    embed.add_field(name="Group", value=f'{command.cog.qualified_name}', inline=False)
                    embed.add_field(name="Syntax",
                                    value=f"`{await get_prefix(self.client, ctx.message)}{command.name} {command.signature}`")
                    if command.aliases:
                        embed.add_field(name="Aliases", value=command.aliases, inline=False)
                    embed.set_footer(text=command.description)
                    await ctx.send(embed=embed)
                    return

        embed.set_author(name="CashewBot - ???", icon_url=icon_url)
        embed.add_field(name="Sorry...", value=f"I couldn't find anything matching {help_call}...")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
