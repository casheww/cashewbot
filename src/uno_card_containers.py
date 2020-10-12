import os
from PIL import Image
import random
from typing import List
from src.uno_card_objects import *
from src.uno_errors import *
from typing import Union


class CardContainer:
    """ Base class for places where cards are
        stored at any point in the game. """

    def __init__(self):
        self.cards = []

    def find_card(self, card_name: str) -> Card:
        """ This method should only be used by container.pull_cards . """
        for card in self.cards:
            if card_name == card.name:
                return card
        raise CardNotFound("You can't play cards you aren't holding."
                           "Card syntax: red.1, blue.pickup."
                           "Wild cards: misc.wild4 green")

    def add_cards(self, cards: List[Card]):
        """ Adds cards to the container. """
        self.cards.extend(cards)
        return None

    def pull_card(self, card_name: str) -> Union[NumberCard, PowerCard]:
        """ Removes a card from the container and returns it. """
        target_card = self.find_card(card_name)

        return self.cards.pop(self.cards.index(target_card))


class Player(CardContainer):
    def __init__(self, member_id: int, channel_id: int, guild_id: int):
        super().__init__()
        self.member_id = member_id
        self.channel_id = channel_id
        self.guild_id = guild_id

    def get_hand_text(self):
        return ", ".join(f"`{c.name}`" for c in self.cards)

    def get_hand_image(self):
        path_list = [c.img_path for c in self.cards]
        image_list = [Image.open(fp) for fp in path_list]
        fp = f"src/uno-temp/{self.guild_id}{self.member_id}.png"

        img = Image.new(
            "RGBA", ((143 + 10) * len(image_list), 214), (1, 0, 0, 0))
        img.paste(image_list.pop(0))
        img.save(fp)

        for image in image_list:
            img = Image.open(fp)
            box = ((143 + 10) * (image_list.index(image) + 1), 0)
            img.paste(image, box)
            img.save(fp)

        img.save(fp)
        return fp


class Pond(CardContainer):
    """ Where cards go after they're played. There should only
        ever be one card here. Previous card goes to the deck. """

    def __init__(self):
        super().__init__()
        self.top_card = None
        self.top_colour = None
        self.top_value = None

    def add_cards(self, cards: List[Card]):
        raise PondOverflow

    def add_card(self, card: Card):
        """ Adds a card to the Pond. All the checks regarding
            whether a card is suitable to be played are performed here. """
        power_effect = ""

        if self.top_card is None:
            pass

        elif isinstance(card, NumberCard):
            if card.colour == self.top_colour or card.number == self.top_value:
                pass    # valid - number card
            else:
                raise IncorrectCard

        elif isinstance(card, PowerCard):
            if card.colour == "misc":
                ...    # valid - wild card
                power_effect = card.power
            elif card.colour == self.top_colour or card.power == self.top_value:
                ...    # valid - power card
                power_effect = card.power

            else:
                raise IncorrectCard
        else:
            raise IncorrectCard

        c = card.to_colour if hasattr(
            card, "to_colour") and card.to_colour is not None else card.colour    # forgive me
        v = card.power if hasattr(card, "power") else card.number
        self.edit_top(card, c, v)

        if len(self.cards) >= 210:      # 216-(216%7)=216-6= 210
            top = self.top_card
            overflow = self.cards
            self.cards = [top]
        else:
            overflow = []

        return overflow, power_effect

    def edit_top(self, card, colour, value):
        self.cards.append(card)
        self.top_card = card

        self.top_colour = colour
        self.top_value = value


class Deck(CardContainer):
    def __init__(self):
        super().__init__()

        # range(4) instead of range(2)? 2 decks -> more players

        for num_card in os.listdir("src/uno-cards/numbers"):
            for i in range(4):
                self.cards.append(NumberCard(num_card[:-4]))
        for pow_card in os.listdir("src/uno-cards/powers"):
            for i in range(4):
                self.cards.append(PowerCard(pow_card[:-4]))

    def draw(self, number: int) -> List[Card]:
        """ Returns a list of random Cards and removes
            them from the Deck. """
        card_list = []
        for i in range(number):
            card = random.choice(self.cards)
            self.cards.remove(card)
            card_list.append(card)
        return card_list

    def pull_random_card(self) -> Card:
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card
