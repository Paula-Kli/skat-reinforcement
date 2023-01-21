import os
import random
import time
from typing import Optional

import players.trump_strategies
from players import RandomPlayer, Player, get_player
from skat_game import PlayerParty, SkatGame
from observers import HumanObserver

# if you want to try playing yourself evaluate: play_skat_for_eval(HumanPlayer(input("What's your name? ")), RandomPlayer("Random 1"), RandomPlayer("Random 2"), random.randint(0, 2))


def game_filename(prefix: str, soloist: Player, team: list[Player], add_timestamp=False):
    time_stamp = time.strftime("-%Y%m%d-%H%M%S-") if add_timestamp else ""
    return f"{prefix}-{time_stamp}{soloist}-vs-{team[0]}-{team[1]}.tsv"

def play_skat_for_eval(
        player1: Player,
        player2: Player,
        player3: Player,
        soloist: int,
        observe_player: Optional[int] = None,
        random_generator=random.Random(),
        verbose: Optional[bool] = True) -> list[int]:
    game = SkatGame(rand_gen=random_generator)
    players = [player1, player2, player3]
    for player_id, player in enumerate(players):
        for observer in player.observers:
            game.add_observer(observer, player_id)
    if observe_player is not None:
        game.add_observer(HumanObserver(), observe_player)
    trump, skat = players[soloist].choose_trump_and_skat(game.hands[soloist], game.skat)
    game.set_bid_results(trump, soloist, skat)

    while not game.done:
        player = players[game.current_player]
        card = player.next_card(game.current_hand, game.current_valid_cards)
        game.play_card(card)

    winning_party = game.winning_party()
    winners = [player for player_id, player in enumerate(players) if game.player_parties[player_id] == winning_party]
    if verbose:
        print(f"{' and '.join(str(winner) for winner in winners)} won with {game.points[winning_party]} points")
    return game.points

def log_stats(
        runs,
        log_interval=0,
        soloist=None,
        opponents=None,
        seed=None,
        create_log_file=True,
        log_file_prefix=None,
        timestamp=True,
        directory=None,
        # Eiter None for no filtering or a list of run IDs
        filter_runs=None,
        print_details=False,
) -> str:
    if soloist is None:
        soloist = RandomPlayer("RANDOM_PLAYER", seed=seed)

    if opponents is None:
        opponents = [RandomPlayer("RANDOM_PLAYER", seed=seed), RandomPlayer("RANDOM_PLAYER", seed=seed)]

    random_generator = random.Random(seed)
    acc_reward = 0
    solo_wins = 0

    prefix = 'stats' if log_file_prefix is None else log_file_prefix
    if directory is not None:
        file_name = f"logs/{directory}/{game_filename(prefix, soloist, opponents, timestamp)}"
        os.makedirs(f"logs/{directory}", exist_ok=True)
    else:
        file_name = f"logs/{game_filename(prefix, soloist, opponents, timestamp)}"

    if create_log_file:
        with open(file_name, "a") as stats_file:
            stats_file.write(f"run\ttotal_reward\n")

    for run in range(runs):
        if filter_runs is None or run in filter_runs:
            total_reward = play_skat_for_eval(soloist, opponents[0], opponents[1], soloist=0,
                                              observe_player=0 if print_details else None,
                                              random_generator=random_generator,
                                              verbose=False)[PlayerParty.soloist]
            if create_log_file:
                with open(file_name, "a") as stats_file:
                    stats_file.write(f"{run}\t{total_reward}\n")
            acc_reward += total_reward
            if total_reward > 60:
                solo_wins += 1
            if log_interval > 0 and run % log_interval == 0 and filter_runs is None:
                print(
                    f"Finished run: {run}, Average Reward: {acc_reward / (run + 1)}, Solo Win Chance: {solo_wins * 100 / (run + 1)}%,"
                    f"Simulation Completed: {(run + 1) * 100 / runs}%")
        else:
            SkatGame(rand_gen=random_generator)

    if filter_runs is None:
        print(f"\nRuns: {runs}, Average Reward: {acc_reward / runs}, Solo Win Chance: {solo_wins * 100 / runs}%")

    return file_name


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Simulate skat game with the specified players",
                            prog="python -m skat_statistics")
    parser.add_argument("--soloist", type=str, default="SimplePlayerV1",
                        help="player name or path to play as soloist")
    parser.add_argument("--defender", type=str, default="SimplePlayerV1",
                        help="player name or path to play as defender")
    parser.add_argument("--trump-strategy", type=str, default="SuitAmountTrumpStrategy",
                        help="the trump strategy to use for non-model players (default: SuitAmountTrumpStrategy)")
    parser.add_argument("--game-count", type=int, default=5000,
                        help="how many games to play (default: 5000)")
    parser.add_argument("--seed", type=int, default=1337,
                        help="the seed for the played games and the players (default: 1337)")
    parser.add_argument("--replay-score", type=int, default=-1,
                        help="If set, game details for all games above or equal to the score are printed.")

    args = parser.parse_args()

    trump_strategy = getattr(players.trump_strategies, args.trump_strategy)()
    soloist = get_player(args.soloist, seed=args.seed, trump_strategy=trump_strategy)
    defender = get_player(args.defender, seed=args.seed, trump_strategy=trump_strategy)

    print(f"Logging stats for\n\tsoloist: {soloist}\n\tdefender: {defender}")

    results = log_stats(
        args.game_count,
        args.game_count / 10,
        soloist,
        [defender, defender.clone()],
        args.seed,
        create_log_file=True)

    if args.replay_score >= 0:
        print(f"\n--------- REPLAY RUNS WITH SCORE {args.replay_score} OR HIGHER ---------")
        print(f"Replaying games for\n\tsoloist: {soloist}\n\tdefender: {defender}")

        filtered = []
        with open(results, "r") as stats_file:
            for line in stats_file.readlines()[1:]:
                run_str, reward_str = line.split('\t')
                reward = int(reward_str)
                if reward >= args.replay_score:
                    filtered.append(int(run_str))

        print(f"Replaying {len(filtered)} games...")
        print("")
        log_stats(
            args.game_count,
            args.game_count / 10,
            soloist,
            [defender, defender.clone()],
            args.seed,
            create_log_file=False,
            filter_runs=filtered,
            print_details=True,
        )


if __name__ == "__main__":
    main()
