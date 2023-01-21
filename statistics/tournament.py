import os
import time

import players.trump_strategies
from players import Player, get_player
from skat_statistics import log_stats, game_filename
from statistics.visualization.tournament_heatmap_visualization import print_tournament_heatmap, tournament_heatmap


def find_existing_stats(log_dirs: list[str], soloist: Player, team: list[Player]):
    filename = game_filename("tournament", soloist, team)
    for log_dir in log_dirs:
        filepath = f"{log_dir}/{filename}"
        if os.path.isfile(filepath):
            return filepath


# Return is in the following layout:
# Each row contains all log file paths for one soloist.
# Each cell in a row contains the game logs against one defender team
def tournament(
        solo_players: list[Player],
        team_players: list[Player],
        num_games: int,
        seed: int,
        tournament_name=None,
        reuse_dirs: list[str] = None,
) -> list[list[str]]:
    results = []
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    for soloist in solo_players:
        row = []
        for defender in team_players:
            team = [defender, defender.clone()]
            log_filename = find_existing_stats(reuse_dirs, soloist, team) if reuse_dirs else None

            if log_filename:
                print(f"Reusing results for soloist {soloist} vs. team of {defender} from old tournament")
                row.append(log_filename)
            else:
                print(f"Simulating soloist {soloist} vs. team of {defender}")
                tournament_suffix = "" if tournament_name is None else f"-{tournament_name}"
                row.append(log_stats(
                    num_games,
                    log_interval=num_games / 10,
                    soloist=soloist,
                    opponents=team,
                    seed=seed,
                    create_log_file=True,
                    log_file_prefix="tournament",
                    directory=f"{timestamp}{tournament_suffix}",
                    timestamp=False
                ))
        results.append(row)
    return results


def tournament_results_files(
        directory: str,
        solo_players: list[str],
        team_players: list[str],
):
    results = []
    for solo_name in solo_players:
        row = []
        for defender_name in team_players:
            row.append(f"{directory}/tournament-{solo_name}-vs-{defender_name}-{defender_name}.tsv")
        results.append(row)
    return results


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Run a tournament with the specified players",
                            prog="python -m statistics.tournament")
    parser.add_argument("--soloists", nargs='+', default=["RandomPlayer", "SimplePlayerV1", "AdvancedPlayer"],
                        help="list of player names or paths to play as soloist")
    parser.add_argument("--soloist-names", nargs="+", default=None, help="custom player names for visualization purposes")
    parser.add_argument("--defender-names", nargs="+", default=None,
                        help="custom player names for the defender for visualization purposes")
    parser.add_argument("--defenders", nargs='+', default=["RandomPlayer", "SimplePlayerV1", "AdvancedPlayer"],
                        help="list of player names or paths to play as defender")
    parser.add_argument("--trump-strategy", type=str, default="SuitAmountTrumpStrategyBetterSkat",
                        help="the trump strategy to use for non-model players (default: SuitAmountTrumpBetterSkatStrategy)")
    parser.add_argument("--game-count", type=int, default=10_000,
                        help="how many games to play for each round (default: 10000)")
    parser.add_argument("--name", type=str, default=None, help="the name of the tournament")
    parser.add_argument("--seed", type=int, default=1337,
                        help="the seed for the played games and the players (default: 1337)")
    parser.add_argument("--reuse-logs", nargs='+', type=str,
                        help="paths to log dirs from existing tournaments to reduce simulation time")
    parser.add_argument("--visualize", action='store_true', help="set flag to plot heatmaps for winrates and rewards")
    parser.add_argument("--device", "-d", choices=["auto", "cpu", "cuda"], default="auto",
                        help="Device on which to run the model players (default: auto)")

    args = parser.parse_args()

    trump_strategy = getattr(players.trump_strategies, args.trump_strategy)()
    soloists = [get_player(name, seed=args.seed, trump_strategy=trump_strategy, device=args.device) for name in args.soloists]
    if args.soloist_names is not None:
        for (name, soloist) in zip(args.soloist_names, soloists):
            soloist.name = name

    defenders = [get_player(name, seed=args.seed, trump_strategy=trump_strategy, device=args.device) for name in args.defenders]

    if args.defender_names is not None:
        for (name, defender) in zip(args.defender_names, defenders):
            defender.name = name

    logs = tournament(soloists, defenders, args.game_count, args.seed, args.name, args.reuse_logs)
    print_tournament_heatmap([str(p) for p in soloists], [str(p) for p in defenders], logs)

    if args.visualize:
        tournament_heatmap([str(p) for p in soloists], [str(p) for p in defenders], logs, args.name)
