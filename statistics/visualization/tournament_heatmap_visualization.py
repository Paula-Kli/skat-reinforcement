import os
from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def tournament_heatmap(
    soloist_names: list[str],
    team_names: list[str],
    tournament_logs: list[list[str]],
    tournament_name: str
):
    sns.set(font_scale=2)

    results_reward = []
    results_winrate = []
    for index in range(len(tournament_logs)):
        row = tournament_logs[index]
        row_rewards = []
        row_winrates = []
        for cell in row:
            with open(Path(cell), "r") as file:
                lines = file.readlines()[1:]
                total = 0
                won = 0
                for line in lines:
                    _, reward_str = line.split('\t')
                    reward = int(reward_str)
                    if reward > 60:
                        won += 1
                    total += reward
            row_rewards.append(total / len(lines))
            row_winrates.append(won * 100 / len(lines))
        results_reward.append(row_rewards)
        results_winrate.append(row_winrates)

    font = {'size': 35}
    plt.rc('font', **font)
    plt.rc('xtick', labelsize=29)
    plt.rc('ytick', labelsize=29)
    fig, _ = plt.subplots(figsize=(30, 12))

    # Defining index for the dataframe

    idx = [name.replace(" vs. ", "\nvs. ").replace(" with ", "\nwith ") for name in soloist_names]
    idy = [name.replace(" vs. ", "\nvs. ").replace(" with ", "\nwith ").replace(" ", "\n") for name in team_names]

    # Defining columns for the dataframe
    cols = idy

    # Entering values in the index and columns
    # and converting them into a panda dataframe
    reward_df = pd.DataFrame(results_reward, columns=cols, index=idx)
    winrate_df = pd.DataFrame(results_winrate, columns=cols, index=idx)

    ax = sns.heatmap(reward_df, cmap=sns.diverging_palette(20, 140, as_cmap=True), linewidths=0.30, annot=True, center=60)

    plt.show()
    os.makedirs("plots", exist_ok=True)
    fig.savefig(f"plots/tournament-{tournament_name}-rewards.png", dpi=fig.dpi)

    fig2, _ = plt.subplots(figsize=(16, 12))
    wins = sns.heatmap(winrate_df, cmap='RdYlGn', linewidths=0.30, annot=True, center=50, fmt='3.2f')
    plt.xticks(rotation=0)
    for t in wins.texts:
        t.set_text(t.get_text() + "%")
    plt.show()
    fig2.savefig(f"plots/tournament-{tournament_name}-winrates.png", dpi=fig2.dpi)


def print_tournament_heatmap(
        soloist_names: list[str],
        team_names: list[str],
        tournament_logs: list[list[str]]):
    print("{:12s} {:>12s} | ".format("Solo", "Team"), end="")
    for team in team_names:
        print("{:14s} | ".format(team[0:13]), end="")
    print("")
    print("-" * 25, end="")
    print(" | ", end="")
    for _ in team_names:
        print("-" * 14, end="")
        print(" | ", end="")
    print("")

    for index in range(len(tournament_logs)):
        print("{:25s} | ".format(soloist_names[index]), end="")
        row = tournament_logs[index]
        for cell in row:
            with open(Path(cell), "r") as file:
                lines = file.readlines()[1:]
                total = 0
                won = 0
                for line in lines:
                    _, reward_str = line.split('\t')
                    reward = int(reward_str)
                    if reward > 60:
                        won += 1
                    total += reward
                print("{:3.2f} : {:3.2f}% | ".format(total / len(lines), won * 100 / len(lines)), end="")
        print("")
