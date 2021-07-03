import random
from player import Player

class Agent(Player):

    def __init__(self, num_cards, card_dict, cache_limit, discount_factor, epsilon, epsilon_final, anneal):
        """
        num_cards: number of playable cards, should be gameObj.num_unique_cards
        cache_limit: max size for memory cache (where previous (state, predicted_q_val, true_reward) are stored)
        discount_factor: something about a horizon and duration for reward expectation (usually 0.95 to 0.999)
        epsilon: initial probability of choosing to explore over exploit
        epsilon_final: final probability of choosing to explore over exploit
        anneal: amount to decrease epsilon by after each pass through dqn
        """
        super().__init__(card_dict)
        # state: 
        # [num_red_0, num_red_1, ..., num_blue_reverse, num_wild_red, num_wild_yellow, ..., num_wild_draw_4_blue, play_deck[0], ..., play_deck[n]]
        # should be gameObj.num_unique_cards (last two indexes are unassigned wild/wild_draw_4 - handled in game.py)
        # if Agent has any wilds, it will have one of each wild color in its hand (since all are possible states)
        # each neuron/action idx corresponds to same card idx defined in game

        # NOT including entire play deck yet, last idx will be top card on play deck
        self.state = [0] * (num_cards + 1)
        self.cache_limit = cache_limit
        self.cache = [0] * self.cache_limit  # insert() and pop() later
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_final = epsilon_final
        self.anneal = anneal

        # action space:
        # [play_red_0, play_red_1, ..., play_blue_reverse, play_wild_red, play_wild_yellow, ..., play_wild_draw_4_blue]
        # each neuron/action idx corresponds to same card idx defined in game

    def add_card(self, card):
        """
        add card to hand and update count in state
        card: card tuple
        """
        self.cards.append(card)

        # if wild, increment each wild color in state correspondingly
        if card[0] == 58:
            for i in range(4):
                self.state[-1 - (1 + i)] += 1
        elif card[0] == 57:
            for i in range(4):
                self.state[-1 - (5 + i)] += 1
        else:
            self.state[card[0]] += 1

    def remove_card(self, card):
        """
        remove card from hand and update count in state
        card: card tuple (if wild it will have a color assigned - decision returns this for the play deck)
        """
        # handle wild card with assigned color
        # TODO check this 
        if card[1] == "wild_draw_4":
            for i in range(4):
                self.state[-1 - (1 + i)] -= 1
            del self.cards[self.cards.index((1, "wild_draw_4", None))]
        elif card[1] == "wild":
            for i in range(4):
                self.state[-1 - (5 + i)] -= 1
            del self.cards[self.cards.index((0, "wild", None))]
        else:
            self.state[card[0]] -= 1
            del self.cards[self.cards.index(card)]

    def decide_card(self, top_card, dqn_out):
        """
        decide which card to play based on dqn, returns card tuple
        top_card: top card on play deck
        dqn_out: output vector from deep q network
        """
        # first get only cards in agent's hand
        hand_indexes = [card[0] for card in self.cards]
        dqn_valid = [(card_idx, q_val) for card_idx, q_val in enumerate(dqn_out) if card_idx in hand_indexes]

        # valid cards by game rules
        dqn_valid = [card_tuple for card_tuple in dqn_valid if self.is_valid(card_tuple, top_card)]

        if len(dqn_valid) > 0:  # this should always be true
            dqn_valid.sort(key=lambda x: x[1], reverse=True)  # sort max to min predicted q value
            explore_prob = random.random()

            if explore_prob <= epsilon:
                # explore
                action_card_idx = random.choice(dqn_valid)[0]
            else:
                # exploit
                action_card_idx = dqn_valid[0][0]

            # get face value and color of card
            action_tuple = self.card_dict[action_card_idx]

            return (action_card_idx, action_tuple[0], action_tuple[1])

        else:
            return None   # i dont think this should ever happen, but idk might be an edge case somewhere

