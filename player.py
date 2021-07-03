class Player:

    def __init__(self, card_dict):
        """
        card_dict: dictionary mapping unique card index to card value (defined in game.py)
        """
        self.cards = []
        self.card_dict = card_dict

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

    def is_valid(self, card, top_card):
        """
        returns a boolean if card is a valid play given top_card
        card: card tuple in question
        top_card: top card in play deck (the card to match against)
        """
        if card[0] == top_card[0] or card[1] == top_card[1] or card[2] == top_card[2] or card[1] == "wild" or card[1] == "wild_draw_4":
            return True
        else:
            return False

    def has_valid(self, top_card, after_draw=False):
        """
        returns boolean if has a playable card or not
        top_card: card on top of play deck (card to match)
        """
        # it's called efficiency bro, don't have to repeat full search through hand
        if after_draw:
            card = self.cards[-1]  # drawn card will be most recently appended
            return is_valid(card, top_card)
        else:
            for card in self.cards:
                return is_valid(card, top_card)

        return False

