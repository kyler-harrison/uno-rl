class Player:

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """
        called when a card is added to a players hand
        card: three element card tuple defined in game.py
        """
        self.cards.append(card)
    
    def remove_card(self, card):
        """
        called when a card is played
        card: three element card tuple defined in game.py
        """
        del self.cards[self.cards.index(card)]

