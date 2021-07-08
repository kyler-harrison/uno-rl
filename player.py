class Player:

    def __init__(self, card_dict):
        """
        card_dict: dictionary mapping unique card index to card value (defined in game.py)
        """
        self.cards = []
        self.card_dict = card_dict

        # TODO
        asg_wild_indexes = []
        asg_wild4_indexes = []

        for card_idx, card_vals in self.card_dict.items():
            if card_vals == ("wild", None):
                self.hand_wild_idx = card_idx
            elif card_vals == ("wild_draw_4", None):
                self.hand_wild4_idx = card_idx
            elif card_vals[0] == "wild":
                asg_wild_indexes.append(card_idx)
            elif card_vals[0] == "wild_draw_4":
                asg_wild4_indexes.append(card_idx)

        asg_wild_indexes.sort()
        asg_wild4_indexes.sort()
        self.min_wild_idx = asg_wild_indexes[0]
        self.max_wild_idx = asg_wild_indexes[-1]
        self.min_wild4_idx = asg_wild4_indexes[0]
        self.max_wild4_idx = asg_wild4_indexes[-1]

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
            return self.is_valid(card, top_card)
        else:
            for card in self.cards:
                valid = self.is_valid(card, top_card)
                if valid: return True

        return False

