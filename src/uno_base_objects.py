from src.uno_card_containers import *
import discord.channel


class Game:
    def __init__(
            self,
            guild_id: int,
            uno_chat: discord.TextChannel,
            m_c_dict: dict):
        self.guild_id = guild_id
        self.player_list = [
            Player(
                m_id,
                m_c_dict[m_id],
                guild_id) for m_id in m_c_dict.keys()]
        self.uno_chat_id = uno_chat.id
        self.deck = Deck()
        self.pond = Pond()

        random.shuffle(self.player_list)        # random player order
        for p in self.player_list:
            self.draw_from_deck(p.member_id, 7)

        pond_starting_card = self.deck.pull_random_card()
        while pond_starting_card.colour == "misc":
            pond_starting_card = self.deck.pull_random_card()
        self.pond.add_card(pond_starting_card)

    def get_player(self, member_id) -> Player:
        for p in self.player_list:
            if member_id == p.member_id:
                return p
        raise PlayerNotFound

    def get_container(self, name) -> CardContainer:
        if name == "deck":
            return self.deck
        elif name == "pond":
            return self.pond
        else:
            return self.get_player(int(name))

    def move_card(self, start: str, end: str, card_name: str):
        """ Moves a card from one CardContainer to another.
            `start` and `end` should be one of:
            "deck", "pond", or a str discord member ID. """
        start = self.get_container(start)
        end = self.get_container(end)

        # split in case of: `misc.wild colour`
        card = start.pull_card(card_name.split()[0])

        if card_name.startswith("misc"):
            card.to_colour = card_name.split()[1]

        if isinstance(end, Pond):
            overflow, power_effect = end.add_card(card)
            self.deck.add_cards(overflow)
            return power_effect
        else:
            end.add_cards([card])
            return ""

    def draw_from_deck(self, member_id: int, number: int) -> List[Card]:
        player = self.get_player(member_id)

        if len(player.cards) >= 12:
            r = random.choice(player.cards)
            overflow_card = player.cards.pop(player.cards.index(r))
            self.deck.add_cards([overflow_card])

        cards = self.deck.draw(number)
        player.add_cards(cards)
        return cards
