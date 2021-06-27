import random

class Game:

    def __init__(self):
        self.deck = []  # deck of cards that is shuffled and removed from 
        self.play_deck = []  # deck of cards that have been played and added to, in order, will be in agent's state

        # card: (idx int, number or special value str, color str)

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


    def deal(self, players, num):
        """ 
        players is list of player objects (Opponent and Agent only, but game can handle more)
        """
        # TODO deal out initial cards randomly from deck
        # should take in player object to update?
        pass

    def draw(self):
        # TODO pick top card from deck, track global game card counter (reinitialize when hits num cards)
        # should take in player object to update?

        # TODO check length after every draw, may need a reshuffle
        pass
