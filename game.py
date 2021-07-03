import random

class Game:

    def __init__(self, reshuffle=False):
        # deck of cards that is shuffled and removed from 
        self.deck = []  

        # deck of cards that are played, in agent's state
        # keeping all cards played throughout all shuffles
        if not reshuffle: 
            self.play_deck = []  

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


        # color cards
        for color in colors:
            # zero
            self.deck += [(uni_idx, "0", color) for _ in range(uni_idx, uni_idx + num_zero)]
            uni_idx += 1

            # numbers
            for num in range(num_min, num_max):
                for num_count in range(num_nums):
                    self.deck.append((uni_idx, str(num), color))
                uni_idx += 1

            # draw 2
            self.deck += [(uni_idx, "draw_2", color) for _ in range(uni_idx, uni_idx + num_draw_2)]
            uni_idx += 1 

            # reverse
            self.deck += [(uni_idx, "reverse", color) for _ in range(uni_idx, uni_idx + num_reverse)]
            uni_idx += 1

            # skip
            self.deck += [(uni_idx, "skip", color) for _ in range(uni_idx, uni_idx + num_skip)]

        self.cards_remain = len(self.deck)  # countdown when a card is drawn, reshuffle new deck when 0

        # used to define a wild card index once Opponent has decided on color 
        wild_set = [("wild", "red"), ("wild", "yellow"), ("wild", "green"), ("wild", "blue")]
        wild_set += [(f"{elem[0]}_draw_4", elem[1]) for elem in wild_set]
        self.wild_dict = {}
        for wild_tuple in wild_set:
            uni_idx += 1
            self.wild_dict[wild_tuple] = uni_idx
        uni_idx += 1

        # wild cards
        self.deck += [(uni_idx, "wild", None) for _ in range(num_wild)]  
        uni_idx += 1

        # wild draw 4 cards
        self.deck += [(uni_idx, "wild_draw_4", None) for _ in range(uni_idx, uni_idx + num_wild_draw_4)]  

        # number of playable cards (can have multiple of each)
        self.num_unique_cards = uni_idx - 2  # unassigned wilds (last two indexes) are only placeholders

        random.shuffle(self.deck)  # shuffle deck

        # NOTE irl top to bottom of deck will be idx -1..0, so top card on deck is self.deck[-1]
        # doing it this way so that self.deck.pop() removes card tuple from deck and returns it

    def draw(self):
        """ draw top card (i.e. self.deck[-1]) from deck and return card tuple """
        card = self.deck.pop()
        self.cards_remain -= 1

        # reshuffle deck if cards have been played (NOTE this does not clear self.play_deck)
        if self.cards_remain == 0:
            self.__init__(reshuffle=True)

        return card

    def deal(self, players, cards_per):
        """ 
        players is list of player objects (Opponent and Agent only, but game can handle more - well
        as long as len(players) * cards_per doesn't exceed the total number of cards (108))
        """
        for player in players:
            for card_per in range(cards_per):
                card = self.draw()  # cards already randomized, so can just pop from deck
                player.add_card(card)

    def handle_play(self, card):
        self.play_deck.append(card)

