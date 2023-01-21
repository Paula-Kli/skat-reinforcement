from players import RandomPlayer, get_player
from players.trump_strategies import SuitAmountTrumpStrategy
from statistics.tournament import tournament, tournament_results_files
from visualization.tournament_heatmap_visualization import print_tournament_heatmap, tournament_heatmap

# Demo file that shows how to reload files from previous tournaments (e.g. for visualization) but this loading is also included  in CLi

teams = [
    "Random",
    "Simple_v1",
]

solos = [
    "Random",
    "Simple_v1",
    "big_2_001_000",
    "big_3_000_000",
    "big_5_000_000",
    "first_8500000",
    "first_10000000",
    "first_13000000",
    "first_13750000"
]

results = tournament_results_files(
    directory="logs/20220714-172359-first",
    solo_players=solos,
    team_players=teams,
)

tournament_heatmap(
    soloist_names=solos,
    team_names=teams,
    tournament_logs=results,
    tournament_name="first")
