# Reinforcement Learning for Skat

This is a repository that provides a framework for training and evaluating reinforcement learning based models. Therefore,
three rule based Player exist: 
   - RandomPlayer (Chooses one of the valid cards randomly.)
   - SimplePlayerV1 ( When playing the first card in a trick, plays the (valid) card with the highest 
   value (any suit) - except if there still is
       an ace of the chosen suit in the game (and not on the player’s hand). In this case, plays the lowest card of that
       suit. When not playing the first card, plays the (valid) card with the lowest value.)
   - AdvancedPlayer (More complex logic and in contrast to the two other players has a different logic for playing as soloist vs.
      vs. as part of the team and keeps track of all his cards.)

## How to write a configuration for a model to be trained

For defining the parameters for a model to be trained one has to write a configuration . This has
to be provided in `/training/configs.py`.
   The config defines:
   - *name*
   - *optimization algorithm* (chosen from [stable baselines 3](https://stable-baselines3.readthedocs.io/en/master/))
   - *policy algorithm* used (we use MaskablePPO from [sb3_contrib](https://sb3-contrib.readthedocs.io/en/master/))
   - *network architecture*
   - *observer* (specified in `/oberservs`)
   - *positional trump* (will the trump independent of the suit be always at the same position in the input)
   - *win reward* (does the model get a reward for winning a game besides the points itself),
   - *trump strategy* (specified in `/players/trump_strategies.py`)

   Different configs can be found in the `/training/configs.py` file.

## How to train a model against a fixed player

   For starting the training several more arguments need to be specified (can be found in `/training/train.py` or you
   can call the CLI with `python -m training.train`). 
   The most important ones are:
   - *position* (specifying where the trained model will play)
   - *predecessor* (the player playing before the model that will be trained)
   - *successor* (the player playing after the model)
   - *config* (name specified in `/training/configs.py`)
   In addition several other values can be specified like the save-interval or the number of timesteps.
   Thus, a call from the repository root for a basic training could look like:

   `python -m training.train soloist AdvancedPlayer AdvancedPlayer myConfigName`

## How to train a model aginst other models

   To train a model against other fixed models one should use the approach from above.
   We developed a round-robin approach in order to train models one after another. Since in that way all three positions
   get trained we need to specify less. In order to see the arguments have a look at `/training/selftrain.py` or call the
   CLI with `python -m training.selftrain`.
   A call to selftrain three models could look like:

   `python -m training.selftrain myConfigName`

## How to measure model performance

   In order to measure the model performance afterwards there is a tool to create a heatmap from a tournament run from
   different players. You can either find it in `/statistics/tournament.py` or have a look at the CLI with
   `python -m statistics.tournament -h`. The most important arguments are:
   - *soloists*
   - *defenders*
   - *trump-strategy* (the trump strategy used in all games)
   - *game-count*
   - *visualize* (in order to actually see the heatmap, after closing it, it will be saved to `/plots`)
   
