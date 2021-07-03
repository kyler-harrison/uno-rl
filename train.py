import random
from game import Game
from opponent import Opponent
from agent import Agent


def check_card(card, game_obj, player_obj):
    """
    checks for draw_2, skip/reverse, wild_draw_4, draws cards if required
    returns True if next player gets to play False else
    card: card tuple
    game_obj: Game object 
    player_obj: Agent/Opponent object
    """
    can_play = True
    num_draw = 0
    
    if card[1] == "draw_2":
        can_play = False
        num_draw = 2
    elif card[1] == "skip" or card[1] == "reverse":
        can_play = False
    elif card[1] == "wild_draw_4":
        can_play = False
        num_draw = 4
    
    for i in range(num_draw):
        player_obj.add_card(game_obj.draw())

    return can_play


def main():
    # TODO init dqn

    num_games = int(1e4)  # number of full games to simulate (guessing agent will get at least 10 plays each, so num_games*10 is num train iters)
    cards_per_hand = 7

    # TODO make this stuff properties of agent 
    cache_limit = num_games // 10  # max number of previous states to remember, if train iterations = 1e6, this takes about 50 MB
    discount_factor = 0.999  # something about a horizon and when to expect reward, can be tweaked
    epsilon = 1  # decreases throughout training
    epsilon_final = 0.05  # where to stop decreasing explore prob
    anneal = (1 - epsilon_final) / num_games  # amount to decrease epsilon on each train pass

    # training/num_games loop
    for i in range(num_games):
        g = Game()
        opp = Opponent(g.card_dict)
        ag = Agent(g.num_unique_cards, g.card_dict, cache_limit, discount_factor, epsilon, epsilon_final, anneal)

        # deal cards to players and flip first card
        g.deal([opp, ag], cards_per_hand)
        g.handle_play(g.draw())

        # finish init of agent's state
        ag.state[-1] = g.play_deck[-1]

        # ignore first card if wild
        while g.play_deck[-1][1] == "wild" or g.play_deck[-1][1] == "wild_draw_4":
            g.handle_play(g.draw())

        # opp decides card
        opp_card = opp.decide_card(g.play_deck[-1])

        # opp draws card if no valid cards the first decision
        if opp_card == None:
            opp.add_card(g.draw())
            opp_card = opp.decide_card(g.play_deck[-1], after_draw=True)

        # opp plays card 
        if opp_card != None:
            g.handle_play(opp_card)

        game_over = False
        can_play = True

        # main loop of single game
        while not game_over:
            # check for special conditions to see if agent can play
            if opp_card != None:
                can_play = check_card(opp_card, g, ag)
            else:
                can_play = True

            if can_play:
                agent_valid = ag.has_valid(g.play_deck[-1])

                if not agent_valid:
                    ag.add_card(g.draw())
                    agent_valid = ag.has_valid(g.play_deck[-1], after_draw=True)
                
                # agent has playable card, will update dqn and put state in cache
                if agent_valid:
                    ag.state[-1] = g.play_deck[-1]  # state now has counts of cards in agent's hand and top card on play deck

                    # TODO pass state through dqn, obtain real output
                    dqn_out = [0.1, 0.2, 0.3]
                    agent_card, expected_q = ag.decide_card(dqn_out, g.play_deck[-1])

                else:
                    agent_card = None

            else:
                agent_card = None

            if agent_card != None:
                g.handle_play(agent_card)
                ag.remove_card(agent_card)

                if len(ag.cards) == 0:
                    reward = 1
                    game_over = True

                # check for special conditions to see if opp can play
                if not game_over:
                    can_play = check_card(agent_card, g, opp)
            else:
                can_play = True

            if not game_over and can_play:
                # opp decides card
                opp_card = opp.decide_card(g.play_deck[-1])

                # opp draws card if no valid cards the first decision
                if opp_card == None:
                    opp.add_card(g.draw())
                    opp_card = opp.decide_card(g.play_deck[-1], after_draw=True)

                # opp plays card 
                if opp_card != None:
                    g.handle_play(opp_card)

                if len(opp.cards) == 0:
                    reward = -1
                    game_over = False
                else:
                    reward = 0

            if agent_card != None:  # only put in cache if the agent was able to play 
                ag.update_cache(expected_q, reward)
                # TODO rando choose cache tuple and do full pass through dqn

            break
        break


if __name__ == "__main__":
    main()

"""
PSEUDO 

init DQN (input dims = state vector dims, output dims = action space vector dims)
cache_limit = some number that cache size will not exceed
cache = []
discount_factor = value from 0 to 1 (0 means chase immediate reward, 1 means sum of future rewards)
epsilon = 1  # epsilon, annealed over time to 0.1/0.05 where it remains fixed
anneal = something like (1 - final_prob) / (0.1 * total_train_update_iterations)

train loop:
    # may not be appropriate to call this train loop
    # nn params are updated after every play (inside game loop below)
    # this is essentially the "how many games to simulate" loop
    # which basically makes it the train loop

    init Game
    init Opp
    init Agent

    Game deals cards to Opp and Agent
    card drawn from Game deck and moved into play deck

    if Opp has valid card:
        Opp plays card based on top card of play deck (for simplicity Opp always goes first)
    else:
        Opp draws card from game deck

        if card drawn is valid: 
            Opp plays card, opp_valid = True
        else:
            opp_valid = False

    game loop:
        if opp_valid = True:
            check for special gameplay (i.e. skip, reverse, draw 2, wild draw 4) -> update Agent correspondingly
            Agent state/hand/whatever_else is updated with Opp placed card

        if Agent has valid card:
            nn_out = Agent passes state through nn
        else:
            Agent draws card from game deck

            if card drawn is valid:
                agent_valid = True
                nn_out = Agent passes state through nn
            else:
                agent_valid = False
        
        if agent_valid:
            prob = rando choice 0 to 1
            if prob <= explore prob:
                action = card idx of rando valid choice from nn_out
            else:
                action = card idx of max valid choice from nn_out
            expected_reward = nn_out[action]

            Agent plays card idx action (update Game and Agent correspondingly)
            if len(Agent.cards) == 0:
                reward = 1 + discount_factor * max(nn_output)  # win
                break loop

            check for special gameplay

        if Opp has valid card:
            Opp plays card, opp_valid = True
        else:
            Opp draws

            if card drawn valid:
                Opp plays card, opp_valid = True
            else:
                opp_valid = False

        if opp_valid and len(Opp.cards) == 0:
            reward = -1 + discount_factor * max(nn_output)  # loss
            break loop
        
        if agent_valid:
            reward = 0 + discount_factor * max(nn_output)  # continuation of game

            if len(cache) == cache_limit: 
                cache.pop()
            
            cache.append((expected_reward, reward))
            update_pair = rando expected_reward/reward pair from cache
            loss = MSE(update_pair)
            update nn params using SGD or Adam

            epsilon -= anneal

"""
