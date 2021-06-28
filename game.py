import random

class Game:

    def __init__(self):
        self.deck = []  # deck of cards that is shuffled and removed from 
        self.play_deck = []  # deck of cards that have been played and added to, in order, will be in agent's state
        self.cards_drawn = 0
        self.size_deck = 108  # 108 total cards (see below), will be indexed 0..107

        # card format: (idx int, number or special value str, color str)

        # special cards
        num_wild = 4
        num_wild_draw_4 = 4

        # params for each color of cards
        colors = ["red", "yellow", "green", "blue"]
        num_zero = 1
        num_nums = 2  # 2 of each num
        num_min = 1  # cards 1-9 (see num_max below)
        num_max = 10  # 1-9 (10 bc range() is exclusive)
        num_draw_2 = 2
        num_reverse = 2
        num_skip = 2

        # track unique idx
        uni_idx = 0

        # wild cards
        self.deck += [(idx, "wild", None) for idx in range(num_wild)]  
        uni_idx += num_wild

        # wild draw 4 cards
        self.deck += [(idx, "wild_draw_4", None) for idx in range(uni_idx, uni_idx + num_wild_draw_4)]  
        uni_idx += num_wild_draw_4

        # color cards
        for color in colors:
            # zero
            self.deck += [(idx, "0", color) for idx in range(uni_idx, uni_idx + num_zero)]
            uni_idx += num_zero

            # numbers
            for num in range(num_min, num_max):
                for num_count in range(num_nums):
                    self.deck.append((uni_idx, str(num), color))
                    uni_idx += 1

            # draw 2
            self.deck += [(idx, "draw_2", color) for idx in range(uni_idx, uni_idx + num_draw_2)]
            uni_idx += num_draw_2

            # reverse
            self.deck += [(idx, "reverse", color) for idx in range(uni_idx, uni_idx + num_reverse)]
            uni_idx += num_reverse

            # skip
            self.deck += [(idx, "skip", color) for idx in range(uni_idx, uni_idx + num_skip)]
            uni_idx += num_skip

        random.shuffle(self.deck)  # shuffle deck

        # NOTE irl top to bottom of deck will be idx -1..0, so top card on deck is self.deck[-1]
        # doing it this way so that self.deck.pop() removes card tuple from deck and returns it
        # and can just check len(deck) each time to see if you need to shuffle a new deck

    def draw(self):
        """ draw top card (i.e. self.deck[-1]) from deck and return card tuple """
        card_drawn = self.deck.pop()
        self.cards_drawn += 1

        # reshuffle deck if cards have been played (TODO make sure agent has a separate list tracking all cards that won't reset)
        if self.cards_drawn == self.deck_size:
            self.__init__()

        return card_drawn

    def deal(self, players, num):
        """ 
        players is list of player objects (Opponent and Agent only, but game can handle more 
        - well as long as len(players) * cards_per doesn't exceed 108)
        """
        cards_per = 7

        for player in players:
            card = self.draw()  # cards already randomized, so can just pop from deck
            player.add_card(card)

