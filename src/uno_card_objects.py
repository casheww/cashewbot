
class Card:
    """ Represents an Uno card. """
    def __init__(self, name: str):
        self.name = name
        self.colour = name.split('.')[0]
        self.img_path = ""


class NumberCard(Card):
    """ A card with a number value. """
    def __init__(self, name: str):
        super().__init__(name)
        self.number = int(name.split('.')[1])
        self.img_path = f"src/uno-cards/numbers/{name}.png"


class PowerCard(Card):
    """ A card with a special power. """
    def __init__(self, name: str, *, to_colour: str = None):
        super().__init__(name)
        self.power = name.split('.')[1]
        self.to_colour = to_colour
        self.img_path = f"src/uno-cards/powers/{name}.png"
