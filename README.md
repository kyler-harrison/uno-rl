## Reinforcement learning in Uno
This repo contains an implementation of a deep q neural network which aims to play the card game Uno optimally against a hardcoded strategy.

## The rl framework
In an essence, a complete reinforcement learning algorithm is defined by a few vocab words: agent, environment, state, action, value function, and policy (see https://spinningup.openai.com/en/latest/spinningup/rl_intro.html for more detailed information).

**Agent**: defined in src/agent.py

**Environment**: defined in src/game.py

**State**: vector containing a count of each card in agent's hand and the current top card on the play deck (i.e. the card you have to check for matches against).

**Policy**: max valid output of the deep q network if exploiting, random valid output of the deep q network if exploring. The dqn is just a simple feedforward net that takes the state as input and predicts a vector of q-values as output.

**Action**: card to play decided by the output of the policy function (see decide_card() in src/agent.py)

**Value function**: reward after each card play of the agent is defined as 0 if the game continues, 1 if the game is won, -1 if the opponent wins on its next card play.

## Results
As a baseline, an agent that makes random decisions against the hardcoded opponent wins ~31% of the time over the course of 1 million games. After 1 million games of training, the "trained" agent wins ~34% of the time. Success? Not really. Failure? Science. 

## Where do we go from here?
I believe the main impediment to the agent's learning is the delayed reward it recieves. After the agent takes an action, it recieves a reward of 0 if the game continues, 
1 if it wins the game, and -1 if it loses the game. This means that the agent recieves ~47 straight rewards of 0 until the average game terminates (see metrics/1e6_iters/std_out.txt). 
I assume that because the ratio of 0 to non-zero rewards the agent recieves is ~47:1, the neural network essentially optimizes to predict very low q-values in order to minimize MSE, meaning that it does not learn to take optimal actions in order to maximize its future reward. In order to get the network to predict more meaningful outputs, a new reward mechanism that gives non-zero rewards more frequently is necessary. Furthermore, there may be potential in different dqn architectures. It may also help to train for many more iterations, but that requires many moneys.


