import discord
from discord.ext import commands
import ast


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Dev(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cashval(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'client': self.client,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        await eval(f"{fn_name}()", env)
        #    await ctx.send(result)
        await ctx.message.add_reaction('\U00002705')


    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        outstr = "```"
        m_tot = 0
        c_tot = 0

        for g in self.client.guilds:
            outstr += f"{g.name}   -   members:{g.member_count}   -   channels:{len(g.channels)}\n"
            m_tot += g.member_count
            c_tot += len(g.channels)

        outstr += f"\nguilds:{len(self.client.guilds)}   -   members:{m_tot}   -   channels:{c_tot}```"
        await ctx.send(outstr)


def setup(client):
    client.add_cog(Dev(client))
