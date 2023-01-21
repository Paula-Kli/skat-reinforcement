import os

import players
from players import Player, ModelPlayer
from skat_env import PlayerPosition, SkatEnv
from training import configs
from training.train import train_config, add_training_parameters
from training.utility import find_latest_model
from training_config import TrainingConfig

model_dir = "models"


def load_training_steps(training_dir: str):
    return [find_latest_model(f"{training_dir}/{pos.name}")[1] for pos in PlayerPosition]


def self_train(
    config: TrainingConfig,
    bootstrap_player: Player,
    steps_per_generation: int,
    num_timesteps: int,
    batch_size=64,
    device: str = "auto",
    verbose=1,
):
    training_dir = f"{model_dir}/{config}/self_train_{bootstrap_player}_{steps_per_generation}"
    for pos in PlayerPosition:
        os.makedirs(f"{training_dir}/{pos.name}", exist_ok=True)
    trained_steps = load_training_steps(training_dir)
    current_position = PlayerPosition(trained_steps.index(min(trained_steps)))
    prev_position = [PlayerPosition.before_soloist, PlayerPosition.soloist, PlayerPosition.after_soloist]
    next_position = [PlayerPosition.after_soloist, PlayerPosition.before_soloist, PlayerPosition.soloist]

    while trained_steps[current_position] < num_timesteps:
        before_player_path, _ = find_latest_model(f"{training_dir}/{prev_position[current_position].name}")
        after_player_path, _ = find_latest_model(f"{training_dir}/{next_position[current_position].name}")
        before_player = ModelPlayer(before_player_path, device=device) if before_player_path else bootstrap_player.clone()
        after_player = ModelPlayer(after_player_path, device=device) if after_player_path else bootstrap_player.clone()
        agent_dir = f"{training_dir}/{current_position.name}"
        print(f"Training {current_position}.")
        train_config(
            config, current_position, before_player, after_player,
            num_timesteps=steps_per_generation, save_interval=steps_per_generation,
            batch_size=batch_size, device=device, verbose=verbose,
            training_dir=agent_dir
        )

        trained_steps[current_position] += steps_per_generation
        current_position = next_position[current_position]


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Train a Skat agent.", prog="python -m training.selftrain")

    parser.add_argument("config", choices=configs.names(), help="The name of a config to use.")
    parser.add_argument("--bootstrap-player", type=str, default="RandomPlayer",
                        help="The player that is used as bootstrap player when no model exists yet.")
    training_parameters = parser.add_argument_group("training parameters")
    training_parameters.add_argument("--steps-per-gen", "-g", type=int, default=250_000,
                                     help="How many steps to train each model in each generation (default: 250_000.")
    add_training_parameters(training_parameters)
    args = parser.parse_args()

    config = configs.get(args.config)

    self_train(
        config,
        players.get_player(args.bootstrap_player),
        num_timesteps=args.timesteps,
        steps_per_generation=args.steps_per_gen,
        batch_size=args.batch_size,
        device=args.device,
        verbose=args.verbosity,
    )


if __name__ == "__main__":
    main()

