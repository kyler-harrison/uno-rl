from player import Player

class Opponent(Player):

    def __init__(self, card_dict):
        super().__init__(card_dict)

        # reverse mapping for wilds in card dictionary (used in decide_card)
        self.wild_dict = {}
        for card_idx, value_tuple in self.card_dict.items():
            if card_idx != self.hand_wild_idx and card_idx != self.hand_wild4_idx:
                if value_tuple[0] == "wild" or value_tuple[0] == "wild_draw_4":
                    self.wild_dict[value_tuple] = card_idx

    def decide_card(self, top_card, after_draw=False):
        """
        implements opponent strategy defined in what.txt, calls play_card()
        top_card: the top card on the play deck (defined in game.py)
        after_draw: if player has already searched and drew a card, true
        """

        # after draw, know that only one match is possible, so whichever card matches first is the only option
        if after_draw == True:
            # drawn card will be the most recently appended (as long as gameplay defined this way)
            card = self.cards[-1]  

            if card[2] == top_card[2] and top_card[2] != None:  # i dont think this None check is necessary given that wild will have color assigned
                # color
                self.remove_card(card)
                return card

            elif card[1] == top_card[1] and top_card[2] != None:
                # suit
                self.remove_card(card)
                return card

            elif card[1] == "wild_draw_4":
                max_color = self.__pick_color()

                if max_color == None:
                    return None

                self.remove_card(card)
                return (self.wild_dict[(card[1], max_color)], card[1], max_color)

            elif card[1] == "wild":
                max_color = self.__pick_color()

                if max_color == None:
                    return None

                self.remove_card(card)
                return (self.wild_dict[(card[1], max_color)], card[1], max_color)

            else:
                return None

        # first check for color match
        color_match = False
        color_matches = [] 

        for card in self.cards:
            if card[2] == top_card[2] and card[1] != "wild" and card[1] != "wild_draw_4":
                color_match = True
                color_matches.append(card)

        if color_match:
            # first search for draw_2
            for i, match in enumerate(color_matches):
                if match[1] == "draw_2":
                    self.remove_card(match)
                    return match

            # then search for skip/reverse 
            for i, match in enumerate(color_matches):
                if match[1] == "skip" or match[1] == "reverse":
                    self.remove_card(match)
                    return match

            # check for any color match
            match = color_matches.pop()
            self.remove_card(match)
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
                    self.remove_card(match)
                    return match

            # then search for skip/reverse 
            for i, match in enumerate(suit_matches):
                if match[1] == "skip" or match[1] == "reverse":
                    self.remove_card(match)
                    return match

            # if no specials, pop will return a number card that matches the
            match = suit_matches.pop()
            self.remove_card(match)
            return match 

        # check for wild cards

        selected_wild4 = self.__select_wild("wild_draw_4")

        if selected_wild4 != None:
            return selected_wild4

        selected_wild = self.__select_wild("wild")

        if selected_wild != None:
            return selected_wild

        # no valid card found
        return None
    
    def __select_wild(self, wild_type):
        """ selects wild card with assigned color """

        for card in self.cards:
            if card[1] == wild_type:
                max_color = self.__pick_color()

                # this shouldn't happen
                if max_color == None:
                    return None

                self.remove_card(card)
                return (self.wild_dict[(card[1], max_color)], card[1], max_color)


    def __pick_color(self):
        """ selects max occurring color (used for selection of wild card) """

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
        
        # this happens if hand is all wilds or you only have one card
        if max_color == None:
            # just choosing red bc i dont want to import random
            return "red" 

        return max_color


