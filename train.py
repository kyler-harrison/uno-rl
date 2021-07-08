import random
import torch
import statistics as stat
import time
from game import Game
from opponent import Opponent
from agent import Agent
from dqn import DQN


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
    start = time.time()
    num_games = int(1e3)  # number of full games to simulate (guessing agent will get at least 10 plays each, so num_games*10 is ~train_iters)
    cards_per_hand = 7
    kill_after = 200  # after running 1000 games, the mean number of plays (looks for each player) with an untrained agent was ~85-100

    cache_limit = num_games // 10  # max number of previous states to remember, if train iterations = 1e6, this takes about 50 MB
    discount_factor = 0.999  # something about a horizon and when to expect reward, can be tweaked
    epsilon = 1  # decreases throughout training
    epsilon_final = 0.05  # where to stop decreasing explore prob
    anneal = (1 - epsilon_final) / num_games  # amount to decrease epsilon on each train pass

    # TODO these are redefined in train loop below, should create reset functions or reorganize somehow 
    g = Game()
    ag = Agent(g.num_unique_cards, g.card_dict, cache_limit, discount_factor, epsilon, epsilon_final, anneal)

    state_size = g.num_unique_cards + 1  # playable cards + 1 card on top of play deck
    action_size = g.num_unique_cards  # playable cards

    # init deep q network (it's just a simple feedforward bro)
    dqn = DQN(state_size, action_size)

    play_counts = []

    # training/num_games loop
    for i in range(num_games):
        g = Game()
        opp = Opponent(g.card_dict)
        ag = Agent(g.num_unique_cards, g.card_dict, cache_limit, discount_factor, epsilon, epsilon_final, anneal)

#        print("=======================================================================")
#        print(f"game #{i}")

        # deal cards to players and flip first card
        g.deal([opp, ag], cards_per_hand)
        g.handle_play(g.draw())

        # ignore first card if wild
        while g.play_deck[-1][1] == "wild" or g.play_deck[-1][1] == "wild_draw_4":
            g.handle_play(g.draw())

#        print(f"agent cards: {ag.cards}")
#        print(f"top card: {g.play_deck[-1]}")

        # finish init of agent's state
        ag.state[-1] = g.play_deck[-1][0]
#        print(f"agent state: {ag.state}")

        # opp decides card
        opp_card = opp.decide_card(g.play_deck[-1])
#        #print(f"\nfirst opp decision: {opp_card}")

        # opp draws card if no valid cards found 
        if opp_card == None:
            opp.add_card(g.draw())
#            #print(f"opp cards after draw: {opp.cards}")
            opp_card = opp.decide_card(g.play_deck[-1], after_draw=True)
#            #print(f"second opp decision: {opp_card}")

        # opp plays card 
        if opp_card != None:
            g.handle_play(opp_card)
#            #print(f"opp cards: {opp.cards}")
#            #print(f"opp plays {opp_card}")
#            #print(f"agent cards: {ag.cards}")
#            print(f"top card: {g.play_deck[-1]}")

        game_over = False
        can_play = True
        play_count = 0  # used to ensure that game doesn't take a disproportionate amount of time

        # main loop of single game
        while not game_over:
            # check for special conditions to see if agent can play
            if opp_card != None:
                can_play = check_card(opp_card, g, ag)
            else:
                can_play = True

#            print(f"\ncan agent play? {can_play}")
#            print(f"agent cards: {ag.cards}")

            if can_play:
                agent_valid = ag.has_valid(g.play_deck[-1])
#                print(f"first does agent have a valid card? {agent_valid}, checked against top card = {g.play_deck[-1]}")

                if not agent_valid:
                    ag.add_card(g.draw())
                    agent_valid = ag.has_valid(g.play_deck[-1], after_draw=True)
#                    print(f"second does agent have a valid card? {agent_valid}, checked against top card = {g.play_deck[-1]} with after_draw=True")

                
                # agent has playable card, will update dqn and put state in cache
                if agent_valid:
                    ag.state[-1] = g.play_deck[-1][0]  # state now has counts of cards in agent's hand and top card on play deck
#                    print(f"agent state: {ag.state}")

                    # forward pass through network, outputs are the predicted q values
                    dqn_out = dqn.forward(torch.tensor([float(num) for num in ag.state]))  
#                    print(f"dqn outputs:\n{dqn_out}")

                    agent_card, ag_hand_card = ag.decide_card(g.play_deck[-1], dqn_out)  
#                    print(f"agent card decision (play card, hand card): {agent_card}, {ag_hand_card}")

                else:
                    agent_card = None
#                    print(f"agent_card: {None}")

            else:
                agent_card = None
#                print(f"agent_card: {None}")

            if agent_card != None:
                g.handle_play(agent_card)
#                #print(f"agent plays: {agent_card}")
#                print(f"top_card: {g.play_deck[-1]}")
                ag.remove_card(ag_hand_card)

                if len(ag.cards) == 0:
                    reward = 1.0
                    reward_vector = [0.0] * action_size  # TODO probs dont need to assign this each time but im 2 tired to make do better
                    reward_vector[agent_card[0]] = reward
                    game_over = True
#                    print(f"reward vector: {reward_vector}")
#                    print("\nGAME OVER, agent wins")

                # check for special conditions to see if opp can play
                if not game_over:
                    can_play = check_card(agent_card, g, opp)
#                    print(f"\ncan opp play? {can_play}")

            else:
                can_play = True
#                print(f"\ncan opp play? {can_play}")

            if not game_over and can_play:
                # opp decides card
                opp_card = opp.decide_card(g.play_deck[-1])

#                #print(f"first opp decision: {opp_card}")

                # opp draws card if no valid cards the first decision
                if opp_card == None:
                    opp.add_card(g.draw())
#                    #print(f"opp cards after draw: {opp.cards}")
                    opp_card = opp.decide_card(g.play_deck[-1], after_draw=True)
#                    #print(f"second opp decision: {opp_card}")

                # opp plays card 
                if opp_card != None:
                    g.handle_play(opp_card)
#                    #print(f"opp cards: {opp.cards}")
#                    #print(f"opp plays {opp_card}")
#                    #print(f"agent cards: {ag.cards}")
#                    print(f"top card: {g.play_deck[-1]}")

                    # only update network if the agent was able to play 
                    if len(opp.cards) == 0 and agent_card != None:
                        game_over = True
                        reward = -1.0
                        reward_vector = [0.0] * action_size
                        reward_vector[agent_card[0]] = reward
#                        print(f"\nGAME OVER, opp wins")

            play_count += 3  # opp has a look, agent has a look, opp has a look

            if play_count > kill_after:
                game_over = True

                if agent_card != None:
                    reward = -1.0
                    reward_vector = [0.0] * action_size
                    reward_vector[agent_card[0]] = reward

            # only update network if the agent was able to play 
            if agent_card != None:  
                if not game_over:
                    reward = 0.0
                    reward_vector = [0.0] * action_size
                    reward_vector[agent_card[0]] = reward

                ag.update_cache(dqn_out, torch.tensor(reward_vector))
#                #print(f"\nagent cache:\n{ag.cache}")

                # choose output/reward from agent's history (avoiding correlated states)
                cache_updater = random.choice(ag.cache)
                cache_expected = cache_updater[0]
                cache_real = cache_updater[1]

                dqn.compute_loss(cache_expected, cache_real)
                del ag.cache[ag.cache.index(cache_updater)]
#                print(f"\ndqn loss = {dqn.loss}")
                dqn.update_params()
        
        play_counts.append(play_count)
#        print("=======================================================================")

    print(f"greatest plays = {max(play_counts)}")
    end = time.time()
    print(f"{end - start} sec for {num_games} games")
       

if __name__ == "__main__":
    main()

