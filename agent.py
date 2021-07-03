class Agent(Player):

    def __init__(self, num_cards):
        """
        num_cards: number of playable cards, should be gameObj.num_unique_cards
        """
        super().__init__()
        # state: 
        # [num_red_0, num_red_1, ..., num_blue_reverse, num_wild_red, num_wild_yellow, ..., num_wild_draw_4_blue, play_deck[0], ..., play_deck[n]]
        # should be gameObj.num_unique_cards (last two indexes are unassigned wild/wild_draw_4 - handled in game.py)
        # if Agent has any wilds, it will have one of each wild color in its hand (since all are possible states)
        # each neuron/action idx corresponds to same card idx defined in game

        # NOT including entire play deck yet, last idx will be top card on play deck
        self.state = [0] * (num_cards + 1)

        # action space:
        # [play_red_0, play_red_1, ..., play_blue_reverse, play_wild_red, play_wild_yellow, ..., play_wild_draw_4_blue]
        # each neuron/action idx corresponds to same card idx defined in game

    def agent_add(self, card):
        """
        add card to hand and update count in state
        card: card tuple
        """
        self.add_card(card)
        self.state[card[0]] += 1

    def agent_remove(self, card):
        """
        remove card from hand and update count in state
        card: card tuple
        """
        self.remove_card(card)
        self.state[card[0]] -= 1

    def decision(self):
        """
        im getting to it
        """
        pass
