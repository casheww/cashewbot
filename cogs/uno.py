import asyncio
import functools
import discord
from discord.ext import commands
from custom_checks import uno_enabled,\
            uno_player_channel, uno_current_player,\
            uno_game_in_progress, uno_game_not_in_progress
import db_interface, json
import src.uno_base_objects as uno_base


def get_uno_colour(top_card: uno_base.Card) -> int:
    colour_dict = {"blue": 0x5555ff, "green": 0x55aa55, "red": 0xff5555, "yellow": 0xffaa00}
    try:
        colour = colour_dict[top_card.colour]
    except KeyError:
        top_card: uno_base.PowerCard    # colour is "misc" for wild cards
        colour = colour_dict[top_card.to_colour]
    return colour


class UnoGame(commands.Cog):
    """ In-discord Uno games --- for Dreamers """
    def __init__(self, bot):
        self.bot = bot
        self.bot.uno_games = {}


    async def uno_broadcast(self, game: uno_base.Game, embed: discord.Embed, fp: str = None):
        players = game.player_list
        for p in players:
            channel = self.bot.get_channel(p.channel_id)
            file = discord.File(fp, "image.png")
            embed.set_thumbnail(url="attachment://image.png")
            await channel.send(file=file, embed=embed)
            await asyncio.sleep(0.5)


    async def uno_turn_embed(self, event: str, top_card: uno_base.Card, next_player: uno_base.Player):
        colour = get_uno_colour(top_card)
        user = self.bot.get_user(next_player.member_id)

        embed = discord.Embed(colour=colour, description=event.replace("*", user.mention))
        embed.set_author(name="\u200B", icon_url=user.avatar_url)
        embed.add_field(name="\u200B", value=f"Last card: `{top_card.name}`")
        embed.set_footer(text=f"{user.display_name} has {len(next_player.cards)} cards.")

        fp = top_card.img_path

        return embed, fp


    async def clear_uno(self, game: uno_base.Game, winner=None):
        uno_chat_id = game.uno_chat_id
        player_list = game.player_list
        persist = self.bot.uno_guilds[game.guild_id]

        del self.bot.uno_games[game.guild_id]

        uno_chat = self.bot.get_channel(uno_chat_id)
        e = discord.Embed(colour=0xff5555)
        if winner:
            e.set_author(name=f"\u200B", icon_url=winner.avatar_url)
            e.add_field(name="\u200B", value=f"{winner.mention} WINS! 🎉")
            e.set_footer(text="Thanks for playing! Uno channels will be"
                              "deleted in a few seconds.")
        else:
            e.set_author(name="Game was ended without a winner.")
            e.set_footer(text="Uno channels will be deleted in a few seconds.")

        await uno_chat.send(embed=e)

        for p in player_list:
            await asyncio.sleep(0.5)
            channel = self.bot.get_channel(p.channel_id)
            await channel.send(embed=e)

        await asyncio.sleep(10)
        for p in player_list:
            channel = self.bot.get_channel(p.channel_id)
            await channel.delete()
            await asyncio.sleep(2)

        cat = uno_chat.category
        await uno_chat.delete()
        if not persist:
            await cat.delete()


    @commands.Cog.listener()
    async def on_card_played(self, game: uno_base.Game, *, effect: str = ""):

        for p in game.player_list:
            if len(p.cards) == 0:
                uno_chat = self.bot.get_channel(game.uno_chat_id)
                async with uno_chat.typing():
                    member = self.bot.get_guild(game.guild_id).get_member(p.member_id)
                    await self.clear_uno(game, member)
                return

        start_str = "It's *'s turn!"

        if effect == "reverse":
            game.player_list.reverse()

        else:
            prev_p = game.player_list.pop(0)        # naturally cycle players
            game.player_list.append(prev_p)

            r = 0
            if effect == "pickup":
                r = 2
            elif effect == "wild4":
                r = 4
            for i in range(r):
                game.player_list[0].add_cards([game.deck.pull_random_card()])

            if effect in ["pickup", "wild4", "skip"]:
                prev_p = game.player_list.pop(0)
                game.player_list.append(prev_p)

        embed, fp = await self.uno_turn_embed(start_str, game.pond.top_card, next_player=game.player_list[0])
        await self.uno_broadcast(game, embed, fp)


    @commands.command(description="Toggles Uno functionality for this server. ",
                      brief="Manage Server permission required.\n"
                            "There must be no Uno games in progress.")
    @uno_game_not_in_progress()
    @commands.has_guild_permissions(manage_guild=True)
    async def toggle_uno(self, ctx):
        guild_info = await db_interface.get_guild_data(self.bot.db, ctx.guild.id)

        if 'uno' in guild_info.keys():
            del guild_info['uno']
            del self.bot.uno_guilds[ctx.guild.id]

            await ctx.send("Uno functionality now **disabled** for this server.")

        else:
            guild_info['uno'] = False       # bool represents uno chat persistence toggle
            self.bot.uno_guilds[ctx.guild.id] = False

            await ctx.send(f"Uno functionality now **enabled** for this server!")

        info = json.dumps(guild_info)
        await db_interface.dump_guild_data(self.bot.db, ctx.guild.id, info)


    @commands.group(description="Command group for in-game commands.",
                    aliases=["u"],
                    brief="Uno must be enabled for this server. (`toggle_uno` command). "
                          "This applies to all subcommands.")
    @uno_enabled()
    async def uno(self, ctx):
        ...


    @uno.command(description="Toggles persistence of the Uno chat and "
                             "category after the game is complete. This allows admins "
                             "to mute the category if not participating, and this mute "
                             "will carry over to future games. Yw, Gerog.",
                 brief="Manage Server permission required.")
    async def toggle_persistence(self, ctx):
        guild_info = await db_interface.get_guild_data(self.bot.db, ctx.guild.id)

        current = self.bot.uno_guilds[ctx.guild.id]
        guild_info['uno'] = not current
        self.bot.uno_guilds[ctx.guild.id] = not current
        await ctx.send(f"Uno chat persistence is now **{not current}** for this server.")

        info = json.dumps(guild_info)
        await db_interface.dump_guild_data(self.bot.db, ctx.guild.id, info)


    @uno.command(description="Starts an Uno game. List players and leave a space between each. "
                             "Player can be as ID, mention, name#0001, name, or nickname.",
                 brief="There must be no Uno games in progress.\n"
                       "Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    @uno_game_not_in_progress()
    async def start_game(self, ctx, members: commands.Greedy[discord.Member]):
        can_read_perm = discord.PermissionOverwrite(read_messages=True)
        cannot_read_perm = discord.PermissionOverwrite(read_messages=False)

        async with ctx.typing():

            cat = discord.utils.get(ctx.guild.categories, name="-- Uno --")
            if cat is None:
                cat = await ctx.guild.create_category("-- Uno --",
                                                      reason=f"Uno game started by {ctx.author}.")

            uno_chat_over = {ctx.guild.default_role: cannot_read_perm}
            player_channel_dict = {}

            # to allow for single-player testing games
            members = [members] if isinstance(members, discord.Member) else members

            for m in members:
                uno_chat_over[m] = can_read_perm

                overwrites = {
                    ctx.guild.default_role: cannot_read_perm,
                    ctx.guild.me: can_read_perm,
                    m: can_read_perm,
                }

                c = await cat.create_text_channel(f"{m}-uno", overwrites=overwrites)
                player_channel_dict[m.id] = c.id
                await c.send(f"GL HF, {m.mention}! Let the Uno begin!")

            uno_chat_over[ctx.guild.me] = can_read_perm
            uno_chat = await cat.create_text_channel("uno-chat", overwrites=uno_chat_over)
            await uno_chat.send(f"Welcome to the Uno lobby! @/here")

            game = uno_base.Game(ctx.guild.id, uno_chat, player_channel_dict)
            self.bot.uno_games[ctx.guild.id] = game

            embed = discord.Embed(title="Uno", colour=0xff5555)
            embed.add_field(
                name="Game Details",
                value=f"Host: *{ctx.author.mention}*\n"
                      f"Player count: *{len(members)}*\n"
                      f"Host playing: *{ctx.author in members}*")

            embed.add_field(name="Members",
                            value=", ".join([m.mention for m in members]),
                            inline=False)

            await ctx.send(f"Game is beginning... -> {uno_chat.mention}")
            self.bot.dispatch("card_played", game)
            await uno_chat.send(embed=embed)


    @uno.command(description="Ends the game without a winner.",
                  brief="There must be an Uno game in progress."
                        "Manage Server permission required.")
    @commands.has_guild_permissions(manage_guild=True)
    @uno_game_in_progress()
    async def end_game(self, ctx):
        async with ctx.typing():
            game = self.bot.uno_games[ctx.guild.id]
            await self.clear_uno(game)


    @uno.command(description="Plays a card from your hand. Card format ex.: `blue.1`, `misc.wild colour`.",
                 brief="Must be playing in active Uno game.\n"
                       "Must be used in Uno player channel\n"
                       "Must be your turn.")
    @uno_game_in_progress()
    @uno_player_channel()
    @uno_current_player()
    async def play(self, ctx, *, card_name):
        if card_name.startswith("misc.wild"):
            try:
                card_name.split()[1]
            except IndexError:
                return await ctx.send("Wildcard syntax: `misc.wild colour`, `misc.wild4 colour`")


        game: uno_base.Game = self.bot.uno_games[ctx.guild.id]
        e = discord.Embed(colour=get_uno_colour(game.pond.top_card))
        e.set_author(name="\u200B", icon_url=ctx.author.avatar_url)

        power_effect = game.move_card(str(ctx.author.id), "pond", card_name)
        e.add_field(name="\u200B", value=f"{ctx.author.mention} played card `{card_name}`")

        if power_effect == "" and not card_name.startswith("misc"):
            fp = f"assets/uno-cards/numbers/{card_name}.png"
        else:
            fp = f"assets/uno-cards/powers/{card_name.split()[0]}.png"

        await self.uno_broadcast(game, e, fp)
        self.bot.dispatch("card_played", game, effect=power_effect)


    @uno.command(description="Shows you your hand of cards.",
                 aliases=['hand', 'mycards'],
                 brief="Must be playing in active Uno game.\n"
                       "Must be used in Uno player channel.")
    @uno_game_in_progress()
    @uno_player_channel()
    async def cards(self, ctx):
        game = self.bot.uno_games[ctx.guild.id]
        colour = get_uno_colour(game.pond.top_card)
        player = game.get_player(ctx.author.id)

        func = functools.partial(player.get_hand_image)
        fp = await self.bot.loop.run_in_executor(None, func)
        card_list = player.get_hand_text()

        f = discord.File(fp, "cards.png")
        e = discord.Embed(colour=colour,
                          description=card_list)
        e.set_author(name="\u200B", icon_url=ctx.author.avatar_url)
        e.set_image(url="attachment://cards.png")

        await ctx.send(file=f, embed=e)


    @uno.command(description="Draws a card from the deck.",
                 brief="Must be playing in active Uno game.\n"
                       "Must be used in Uno player channel.\n"
                       "Must be your turn.")
    @uno_game_in_progress()
    @uno_player_channel()
    @uno_current_player()
    async def draw(self, ctx):
        game = self.bot.uno_games[ctx.guild.id]
        new_card = game.draw_from_deck(ctx.author.id, 1)[0]

        e = discord.Embed(colour=get_uno_colour(game.pond.top_card),
                          description=f"New card: `{new_card.name}`")
        e.set_author(name="\u200B", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
        cards_command = self.bot.get_command("uno cards")
        await cards_command.__call__(ctx)

        e.description = f"{ctx.author.mention} has drawn a card."
        # didn't use broadcasting func b/c otherwise info is send to author twice
        for p in game.player_list:
            if p.member_id != ctx.author.id:
                c = self.bot.get_channel(p.channel_id)
                await c.send(embed=e)

        self.bot.dispatch("card_played", game)


def setup(bot):
    bot.add_cog(UnoGame(bot))
