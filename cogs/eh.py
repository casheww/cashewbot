from discord.ext import commands
import traceback as tb


class EH(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        try:
            if hasattr(ctx.command, 'on_error') or hasattr(ctx, 'handled_locally') or \
                    hasattr(ctx.command.parent, 'on_error'):
                return
        except (AttributeError, TypeError):
            pass

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        with open('../log.txt', 'a+', encoding='utf16') as f:
            f.write(f"""--- {error}
            {ctx.author} - {ctx.author.id}
            {ctx.message.content}
            {tb.extract_tb(error.__traceback__)}\n\n""")

        em_dict = {
            commands.ExtensionNotFound: "The extension was not found.",
            commands.ExtensionAlreadyLoaded: "The extension is already loaded.",
            commands.NoEntryPointError: "The extension does not have a setup function.",
            commands.ExtensionFailed: "The extension or its setup function had an execution error.",
            commands.ExtensionNotLoaded: "That extension is not loaded.",

            commands.CommandNotFound: "Sorry, that command doesn't exist. Please try the `help` command.",
            commands.UserInputError: "Hmm... Something you entered wasn't quite right. Try `help [command]`.",
            commands.NotOwner: "Only the owner of the bot can use this command.",
            commands.NoPrivateMessage: "This command can't be used outside of a server.",
        }

        for e in em_dict:
            if isinstance(error, e):
                return await ctx.send(em_dict[e])

        if isinstance(error, commands.CheckFailure):
            if hasattr(ctx, 'custom_check_fail'):
                msg = ctx.custom_check_fail
            else:
                msg = "The requirements to run this command were not satisfied."
            return await ctx.send(msg)

        await ctx.send(tb.extract_tb(error.__traceback__), delete_after=10)
        raise error


def setup(bot):
    bot.add_cog(EH(bot))
