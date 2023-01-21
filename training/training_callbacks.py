import os
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.results_plotter import load_results, ts2xy


# copied and modified from https://stable-baselines.readthedocs.io/en/master/guide/examples.html
class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).
    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contain the file created by the ``Monitor`` wrapper.
    :param save_interval: (int) when should a model get saved
    :param verbose: (int)
    """

    def __init__(self, check_freq: int, log_dir: str, save_interval: int, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_interval = save_interval
        self.log_dir = log_dir
        self.best_model_path = f"{log_dir}/best_model.zip"
        self.best_mean_reward = -np.inf

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

            # Retrieve training reward
            x, y = ts2xy(load_results(self.log_dir), 'timesteps')
            if len(x) > 0:
                # Mean training reward over the last episodes
                rewards: np.ndarray = y[-self.check_freq // 10:]
                mean_reward = np.mean(rewards)
                games_won = np.count_nonzero(rewards > 60) / rewards.size * 100
                self.best_mean_reward = max(self.best_mean_reward, mean_reward)
                if self.verbose > 0:
                    print(f"Num timesteps: {self.num_timesteps}")
                    print(f"Best mean reward: {self.best_mean_reward:.2f} - "
                          f"Last mean reward per episode: {mean_reward:.2f} - Percentage of won games: {games_won:.2f}")

        if self.num_timesteps % self.save_interval == 0:
            regular_save_path = f"{self.log_dir}/{self.num_timesteps:_}"
            if self.verbose > 0:
                print(f"Saving model to {regular_save_path}")
            self.model.save(regular_save_path)

        return True
