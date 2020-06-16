from discord.ext.commands import check


def is_celery():
    def predicate(ctx):
        return ctx.author.id == 508862828103467010
    return check(predicate)
