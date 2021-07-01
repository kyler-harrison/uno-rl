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
        Opp draws card from game deck, if valid play card 

    game loop:
        check for special gameplay (i.e. skip, reverse, draw 2, wild draw 4) -> update Agent correspondingly
        Agent state/hand/whatever_else is updated with Opp placed card
        nn_out = Agent passes state through nn

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

        Opp takes action
        if len(Opp.cards) == 0:
            reward = -1 + discount_factor * max(nn_output)  # loss
            break loop
        
        reward = 0 + discount_factor * max(nn_output)  # continuation of game

        if len(cache) == cache_limit: 
            cache.pop()
        
        cache.append((expected_reward, reward))
        update_pair = rando expected_reward/reward pair from cache
        loss = MSE(update_pair)
        update nn params using SGD or Adam

        explore_prob -= explore_anneal

"""
