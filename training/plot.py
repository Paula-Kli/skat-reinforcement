import sys

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3.common import results_plotter


def moving_average(values: np.ndarray, window: int):
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')


def plot(model_folder: str):
    results_plotter.plot_results(
        [model_folder], None, results_plotter.X_TIMESTEPS, "Skat")
    plt.show()


if __name__ == "__main__":
    # path to model folder
    plot(sys.argv[1])
