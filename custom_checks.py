from discord.ext.commands import check
import json

with open("_keys.gitignore", "r") as f:
    kelb = json.load(f)["kelb_id"]


def is_celery():
    def predicate(ctx):
        return ctx.author.id == int(kelb)
    return check(predicate)


def uno_enabled():
    def predicate(ctx):
        return ctx.guild.id in ctx.bot.uno_guilds
    return check(predicate)


def uno_game_in_progress():
    def predicate(ctx):
        return ctx.guild.id in ctx.bot.uno_games.keys()
    return check(predicate)


def uno_game_not_in_progress():
    def predicate(ctx):
        return ctx.guild.id not in ctx.bot.uno_games.keys()
    return check(predicate)


def uno_player_channel():
    def predicate(ctx):
        game = ctx.bot.uno_games[ctx.guild.id]
        current_player = game.get_player(ctx.author.id)

        if current_player is None:      # member is not in Uno game
            return False

        return current_player.channel_id == ctx.channel.id
    return check(predicate)


def uno_current_player():
    def predicate(ctx):
        game = ctx.bot.uno_games[ctx.guild.id]
        current_player = game.player_list[0]

        return current_player.member_id == ctx.author.id
    return check(predicate)
