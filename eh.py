from discord.ext import commands
import traceback


class EH(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)

        with open('log.txt', 'a+', encoding='utf16') as f:
            f.write(f"""--- {error}
            {ctx.author} - {ctx.author.id}
            {ctx.message.content}
            {traceback.print_exception(error, error, error.__traceback__, 5)}\n\n""")

        em_dict = {
            commands.ExtensionNotFound: "The extension was not found.",
            commands.ExtensionAlreadyLoaded: "The extension is already loaded.",
            commands.NoEntryPointError: "The extension does not have a setup function.",
            commands.ExtensionFailed: "The extension or its setup function had an execution error.",
            commands.ExtensionNotLoaded: "That extension is not loaded.",

            commands.CommandNotFound: "Sorry, that command doesn't exist. Please try the `help` command.",
            commands.UserInputError: "Hmm... Something you entered wasn't quite right. Try `help [command]`.",
            commands.NotOwner: "Only the owner of the bot can use this command.",
            commands.NoPrivateMessage: "This command can't be used outside of a server."
        }

        await ctx.message.add_reaction('\U0000274e')

        for e_name in em_dict:
            if isinstance(error, e_name):
                await ctx.send(em_dict[e_name])
                return

        await ctx.send(error, delete_after=10)


def setup(client):
    client.add_cog(EH(client))
