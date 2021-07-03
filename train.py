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
    # TODO 
    # init dqn

    num_games = int(1e4)  # number of full games to simulate (guessing agent will get at least 10 plays each, so num_games*10 is num train iters)
    cache_limit = num_games // 10  # max number of previous states to remember, if train iterations = 1e6, this takes about 50 MB
    discount_factor = 0.999  # something about a horizon and when to expect reward, can be tweaked
    explore_prob = 1  # decreases throughout training
    explore_final_prob = 0.05  # where to stop decreasing explore prob
    explore_anneal = (1 - explore_final_prob) / num_games  # amount to decrease explore_prob on each train pass
    cards_per_hand = 7

    # training/num_games loop
    for i in range(num_games):
        g = Game()
        opp = Opponent()
        ag = Agent(g.num_unique_cards)

        # deal cards to players and flip first card
        g.deal([opp, ag], cards_per_hand)
        g.handle_play(g.draw())

        # ignore first card if wild
        while g.play_deck[-1] == "wild" or g.play_deck[-1] == "wild_draw_4":
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

        not_game_over = True
        can_play = True

        # main loop of single game
        while not_game_over:
            # check for special conditions to see if agent can play
            if opp_card != None:
                can_play = check_card(opp_card, g, ag)
            else:
                can_play = True

            if can_play:
                #ag.state[]
                pass
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
explore_prob = 1  # epsilon, annealed over time to 0.1/0.05 where it remains fixed
explore_anneal = something like (1 - final_prob) / (0.1 * total_train_update_iterations)

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

            explore_prob -= explore_anneal

"""