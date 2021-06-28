class Player:

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """
        card: three element card tuple defined in game.py
        """
        self.cards.append(card)

