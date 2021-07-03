from player import Player

class Opponent(Player):

    def __init__(self):
        super().__init__()

    def decide_card(self, top_card, wild_dict, after_draw=False):
        """
        implements opponent strategy defined in what.txt, calls play_card()
        top_card: the top card on the play deck (defined in game.py)
        after_draw: if player has already searched and drew a card, true
        wild_dict: mapping of ("wild", "color") to index in state (defined in game.py)
        """

        # after draw, know that only one match is possible, so whichever card matches first is the only option
        if after_draw == True:
            # drawn card will be the most recently appended (as long as gameplay defined this way)
            card = self.cards[-1]  

            if card[2] == top_card[2] and top_card[2] != None:
                # color
                self.remove_card(card)
                return card
            elif card[1] == top_card[1] and top_card[2] != None:
                # suit
                self.remove_card(card)
                return card
            elif card[1] == top_card[1] and top_card[1] == "wild_draw_4":
                # wild draw 4
                self.remove_card(card)
                return card
            elif card[1] == top_card[1] and top_card[1] == "wild":
                # wild
                self.remove_card(card)
                return card
            else:
                return None

        # first check for color match
        color_match = False
        color_matches = [] 

        for card in self.cards:
            if card[2] == top_card[2] and top_card[2] != None:
                color_match = True
                color_matches.append(card)

        if color_match:
            # first search for draw_2
            for i, match in enumerate(color_matches):
                if match[1] == "draw_2":
                    self.remove_card(card)
                    return match

            # then search for skip/reverse 
            for i, match in enumerate(color_matches):
                if match[1] == "skip" or match[1] == "reverse":
                    self.remove_card(card)
                    return match

            # if no specials, pop will return a number card that matches the color
            match = color_matches.pop()
            self.remove_card(card)
            return match 

        # TODO make this a generic fun for the above and the below (redundant)
        # or just dont i mean who cares

        # check for suit match
        suit_match = False
        suit_matches = []

        for card in self.cards:
            if card[1] == top_card[1] and top_card[2] != None:
                suit_match = True
                suit_matches.append(card)

        if suit_match:
            # first search for draw_2
            for i, match in enumerate(suit_matches):
                if match[1] == "draw_2":
                    self.remove_card(card)
                    return match

            # then search for skip/reverse 
            for i, match in enumerate(suit_matches):
                if match[1] == "skip" or match[1] == "reverse":
                    self.remove_card(card)
                    return match

            # if no specials, pop will return a number card that matches the
            match = suit_matches.pop()
            self.remove_card(card)
            return match 

        # check for wild cards
        # and change the color in the wild card from None to the max color
        # index corresponding to wild color in agent's action space should be returned in this tuple

        # TODO redundant, this could be a single function

        for card in self.cards:
            if card[1] == "wild_draw_4":
                max_color = self.__pick_color()

                # this shouldn't happen
                if max_color == None:
                    return None

                self.remove_card(card)
                return (wild_dict[(card[1], max_color)], card[1], max_color)

        for card in self.cards:
            if card[1] == "wild":
                max_color = self.__pick_color()

                # this shouldn't happen
                if max_color == None:
                    return None

                self.remove_card(card)
                return (wild_dict[(card[1], max_color)], card[1], max_color)

        # no valid card found. outside of this scope: draw another card and call opponent's decision() again (if haven't already)
        return None

    def __pick_color(self):
        color_counts = dict.fromkeys(["red", "blue", "green", "yellow"], 0)

        # count each color
        for card in self.cards:
            if card[2] != None:
                color_counts[card[2]] += 1

        # find max occurring color
        max_color = None
        max_count = 0

        for color, count in color_counts.items():
            if count > max_count:
                max_color = color
                max_count = count

        return max_color


