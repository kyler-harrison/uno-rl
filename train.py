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


def write_metrics(file_path, metrics_ls, mode):
    """ write metrics obtained in training to file """
    with open(file_path, mode) as f:
        for met in metrics_ls:
            f.write(f"{met}\n")


def main():
    start = time.time()
    num_games = int(1e6)  # number of full games to simulate (guessing agent will get at least 10 plays each, so num_games*10 is ~train_iters)
    cards_per_hand = 7
    kill_after = 200  # terminate game if plays > this 

    cache_limit = num_games // 10  # max number of previous states to remember, if train iterations = 1e6, this takes about 50 MB
    discount_factor = 0.999  # something about a horizon and when to expect reward, can be tweaked
    epsilon = 1  # decreases throughout training
    epsilon_final = 0.05  # where to stop decreasing explore prob
    anneal = (1 - epsilon_final) / num_games  # amount to decrease epsilon on each train pass

    # throwaway inits for training information
    g = Game()
    ag = Agent(g.num_unique_cards, g.card_dict, cache_limit, epsilon)

    state_size = g.num_unique_cards + 1  # playable cards + 1 card on top of play deck
    action_size = g.num_unique_cards  # playable cards

    # init deep q network (it's just a simple feedforward bro)
    dqn = DQN(state_size, action_size)

    # cumulative metrics
    met_dir = "metrics"
    play_counts = []
    time_ot = []
    loss_ot = []
    reward_ot = []
    play_counts_f = f"{met_dir}/play_counts.txt"
    time_f = f"{met_dir}/train_time.txt"
    loss_f = f"{met_dir}/loss.txt"
    reward_f = f"{met_dir}/reward.txt"
    opp_wins = 0
    ag_wins = 0
    games_killed = 0
    output_every = 1000

    # training loop
    for i in range(num_games):
        train_start = time.time()

        # update agent's explore/exploit prob (TODO should I update this after every backprop instead? will need to change)
        if epsilon > epsilon_final:
            epsilon -= anneal

        g = Game()
        opp = Opponent(g.card_dict)
        ag = Agent(g.num_unique_cards, g.card_dict, cache_limit, epsilon)

        play_count = 0  # used to ensure that game doesn't take a disproportionate amount of time
        loss = None  # prevent incorrect loss output, if agent doesn't get to play: new loss won't be computed in game

        # deal cards to players and flip first card
        g.deal([opp, ag], cards_per_hand)
        g.handle_play(g.draw())

        # ignore first card if wild
        while g.play_deck[-1][1] == "wild" or g.play_deck[-1][1] == "wild_draw_4":
            g.handle_play(g.draw())

        # finish init of agent's state
        ag.state[-1] = g.play_deck[-1][0]

        # opp decides card
        opp_card = opp.decide_card(g.play_deck[-1])

        # opp draws card if no valid cards found 
        if opp_card == None:
            opp.add_card(g.draw())
            opp_card = opp.decide_card(g.play_deck[-1], after_draw=True)

        # opp plays card 
        if opp_card != None:
            g.handle_play(opp_card)

        play_count += 1  # starting play by opp
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
                    ag.state[-1] = g.play_deck[-1][0]  # state now has counts of cards in agent's hand and top card on play deck

                    # forward pass through network, outputs are the predicted q values
                    dqn_out = dqn.forward(torch.tensor([float(num) for num in ag.state]))  

                    agent_card, ag_hand_card = ag.decide_card(g.play_deck[-1], dqn_out)  

                else:
                    agent_card = None

            else:
                agent_card = None

            if agent_card != None:
                g.handle_play(agent_card)
                ag.remove_card(ag_hand_card)

                if len(ag.cards) == 0:
                    reward = 1.0 * discount_factor
                    reward_vector = [0.0] * action_size  # TODO probs dont need to assign this each time but im 2 tired to make do better
                    reward_vector[agent_card[0]] = reward
                    reward_ot.append(reward)
                    ag_wins += 1
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
                        game_over = True
                        opp_wins += 1

                        # only update network if the agent was able to play 
                        if agent_card != None:
                            reward = -1.0 * discount_factor
                            reward_vector = [0.0] * action_size
                            reward_vector[agent_card[0]] = reward
                            reward_ot.append(reward)

            play_count += 2  # agent has a look, opp has a look

            if play_count > kill_after:
                game_over = True
                games_killed += 1

                if agent_card != None:
                    reward = -1.0 * discount_factor
                    reward_vector = [0.0] * action_size
                    reward_vector[agent_card[0]] = reward
                    reward_ot.append(reward)

            # only update network if the agent was able to play 
            if agent_card != None:  
                if not game_over:
                    reward = 0.0
                    reward_vector = [0.0] * action_size
                    reward_vector[agent_card[0]] = reward
                    reward_ot.append(reward)

                ag.update_cache(dqn_out, torch.tensor(reward_vector))

                # choose output/reward from agent's history (avoiding correlated states)
                cache_updater = random.choice(ag.cache)
                cache_expected = cache_updater[0]
                cache_real = cache_updater[1]

                dqn.compute_loss(cache_expected, cache_real)
                loss = dqn.loss.item()
                loss_ot.append(loss)
                del ag.cache[ag.cache.index(cache_updater)]
                dqn.update_params()
        
        # after game completes
        train_end = time.time()
        train_time = train_end - train_start
        time_ot.append(train_time)
        play_counts.append(play_count)

        # TODO write some stuff to file so can output graphs later
        if (i % output_every) == 0 or (i + 1 == num_games):
            print("=======================================================================")
            print(f"game #{i}")
            print(f"game time = {train_time:.5f} sec")
            av_time = stat.mean(time_ot)
            print(f"average game time = {av_time:.5f} sec")
            print()

            av_plays = stat.mean(play_counts)
            print(f"number of total plays = {play_count}")
            print(f"average number of total plays = {av_plays:.5f}")
            print(f"number of opponent wins = {opp_wins}, number of agent wins = {ag_wins}, number of games killed = {games_killed}")
            opp_pct = opp_wins / (i + 1)
            ag_pct = ag_wins / (i + 1)
            kill_pct = games_killed / (i + 1)
            print(f"cumulative opponent win % = {opp_pct:.5f}, cumulative agent win % = {ag_pct:.5f}, cumulative games killed % = {kill_pct:.5f}")
            print()

            print(f"agent explore prob (epsilon) = {ag.epsilon}")
            if loss != None: 
                print(f"agent dqn game loss = {loss:.5f}")
            else:
                print(f"agent dqn dqn game loss was not updated")

            if len(loss_ot) != 0:
                av_loss = stat.mean(loss_ot)
                print(f"average agent dqn loss = {av_loss:.5f}")
            else:
                print("average agent dqn loss could not be computed, dqn loss has yet to be computed")

            print("=======================================================================")
            print()

    # write output files
    write_metrics(play_counts_f, play_counts, 'w')
    write_metrics(loss_f, loss_ot, 'w')
    write_metrics(time_f, time_ot, 'w')
    write_metrics(reward_f, reward_ot, 'w')

    end = time.time()
    total_train_time = end - start
    print("FINAL")
    print(f"total train time for {num_games} games = {total_train_time} sec")
       

if __name__ == "__main__":
    main()

