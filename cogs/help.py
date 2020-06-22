import discord
from discord.ext import commands
from main import get_prefix


hidden_cogs = ['Dev', 'EH']

def command_plural(count):
    if count == 1:
        return 'command'
    else:
        return 'commands'


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(description="Returns a helpful message!")
    async def help(self, ctx, *, help_call=None):
        if ctx.guild:
            embed = discord.Embed(colour=ctx.guild.me.color)
        else:
            embed = discord.Embed(colour=discord.Colour.purple())

        # shows all cogs - ultimate level
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

            embed.set_author(name="CashewBot - Help")
            embed.add_field(name="Command Categories", value=outstr)
            embed.set_footer(text="Try `help category-name`!")
            return await ctx.send(embed=embed)

        # cog level
        for cog in self.client.cogs:
            if cog not in hidden_cogs and help_call.lower() == cog.lower():
                cog_commands = self.client.cogs[cog].get_commands()
                outstr = ""

                for c in cog_commands:
                    if not c.hidden:
                        outstr += f"**{c.qualified_name}** - {c.description}\n\n"

                embed.set_author(name=f"CashewBot - {cog} Category")
                embed.add_field(name="Commands", value=outstr)
                embed.set_footer(text="Try `help command-name`!")
                return await ctx.send(embed=embed)

        # command level
        for command in self.client.commands:
            if help_call == command.qualified_name or help_call in command.aliases:

                if not command.hidden:

                    embed.add_field(name="Parent Category", value=f"{command.cog.qualified_name}", inline=False)

                    if not isinstance(command, commands.Group):
                        embed.set_author(name=f"CashewBot - {command.qualified_name} Command")
                        embed.add_field(name="Syntax",
                                        value=f"`{await get_prefix(self.client, ctx.message)}"
                                              f"{command.name} {command.signature}`")
                        if command.aliases:
                            embed.add_field(name="Aliases", value=command.aliases, inline=False)
                        embed.set_footer(text=command.description)
                        return await ctx.send(embed=embed)

                    else:
                        embed.set_author(name=f"CashewBot - {command.qualified_name} Command Group")

                        outstr = ""
                        for sub in command.commands:
                            outstr += f"**{sub.qualified_name}** - {sub.description}\n\n"

                        embed.add_field(name="Subcommands", value=outstr)
                        return await ctx.send(embed=embed)


        # fallback for no help match
        embed.set_author(name="CashewBot - ???")
        embed.add_field(name="Sorry...", value=f"I couldn't find anything matching {help_call}...")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
