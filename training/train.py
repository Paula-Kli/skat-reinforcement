import os
import time
from typing import Optional

from stable_baselines3.common.monitor import Monitor

import players
from players import Player
from skat_env import SkatEnv, PlayerPosition
from training import configs
from training.utility import find_latest_model
from training_config import TrainingConfig
from training.training_callbacks import SaveOnBestTrainingRewardCallback

model_dir = "models"


def train_config(
    config: TrainingConfig,
    player_position: PlayerPosition,
    predecessor: Player,
    successor: Player,
    num_timesteps=100_000,
    save_interval=250_000,
    batch_size=64,
    device: str = "auto",
    verbose=1,
    training_dir: Optional[str] = None,
):
    training_dir = training_dir or f"{model_dir}/{config}/{player_position.name}_{predecessor}_{successor}"
    os.makedirs(training_dir, exist_ok=True)

    skat_env = SkatEnv(
        player_position, predecessor, successor, config.observer(**config.observer_kwargs), config.trump_strategy())
    env = Monitor(skat_env, f"{training_dir}/{time.strftime('%Y%m%d-%H%M%S')}")

    callback = SaveOnBestTrainingRewardCallback(
        check_freq=10000,
        log_dir=training_dir,
        save_interval=save_interval)

    latest_model, _ = find_latest_model(training_dir)
    if latest_model:
        print(f"Resuming model from: {latest_model}. If this is not intended, please remove old model.")
        model = config.algorithm.load(
            latest_model, env, policy_kwargs=config.policy_kwargs,
            batch_size=batch_size, device=device)
    else:
        model = config.algorithm(
            config.policy, env, policy_kwargs=config.policy_kwargs, verbose=verbose,
            batch_size=batch_size, device=device)

    model.learn(total_timesteps=num_timesteps, callback=callback, log_interval=None, reset_num_timesteps=False)


def add_training_parameters(parser):
    parser.add_argument("--batch-size", "-b", type=int, default=64,
                        help="Batch size for training (default: 64), increase when training on GPU.")
    parser.add_argument("--timesteps", "-n", type=int, default=10_000_000,
                        help="Number of steps after which training stops automatically (default: 10_000_000).")
    parser.add_argument("--device", "-d", choices=["auto", "cpu", "cuda"], default="auto",
                        help="Device on which to run the training (default: auto)")
    parser.add_argument("--verbosity", "-v", choices=[0, 1, 2], default=1,
                        help="The verbosity level (default: 1).")


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Train a Skat agent.", prog="python -m training.train")

    env_args = parser.add_argument_group("training environment")
    env_args.add_argument("position", choices=[pos.name for pos in PlayerPosition],
                          help="The position on which the agent should be trained.")
    env_args.add_argument("predecessor", type=str, help="The player type to sit before the agent.")
    env_args.add_argument("successor", type=str, help="The player type to sit after the agent.")

    config_args = parser.add_argument_group("training config")
    config_args.add_argument("config", choices=configs.names(),
                             help="The name of a config to use.")
    add_training_parameters(parser.add_argument_group("training parameters"))
    parser.add_argument("--save-interval", "-s", type=int, default=100_000,
                        help="Number of steps after which the model is automatically saved (default: 100_000).")

    args = parser.parse_args()

    config = configs.get(args.config)

    train_config(
        config,
        player_position=PlayerPosition[args.position],
        predecessor=players.get_player(args.predecessor, device=args.device),
        successor=players.get_player(args.successor, device=args.device),
        num_timesteps=args.timesteps,
        save_interval=args.save_interval,
        batch_size=args.batch_size,
        device=args.device,
        verbose=args.verbosity,
    )


if __name__ == "__main__":
    main()
