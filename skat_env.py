import os
from enum import IntEnum
from os.path import exists
from random import Random
from typing import Optional, Type

import gym
import numpy as np

from card import Card
from observers import ModelObserver
from players import Player
from players.trump_strategies import TrumpStrategy
from skat_game import SkatGame, PlayerParty


class PlayerPosition(IntEnum):
    soloist = 0
    after_soloist = 1
    before_soloist = 2

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(pos: str):
        try:
            return PlayerPosition[pos]
        except KeyError:
            raise ValueError


class SkatEnv(gym.Env):
    metadata = {"render.modes": ['ansi']}

    def __init__(
        self,
        position: PlayerPosition,
        predecessor: Player,
        successor: Player,
        observer: ModelObserver,
        trump_strategy: TrumpStrategy,
    ):
        self.observer = observer
        self.action_space = self.observer.action_space
        self.observation_space = self.observer.observation_space

        self.game: Optional[SkatGame] = None
        self.other_players = [successor, predecessor]
        self.trump_strategy = trump_strategy
        self.player_id = 2
        self.position = position
        self.party = PlayerParty.soloist if position == PlayerPosition.soloist else PlayerParty.defenders
        self.rand_seed = None
        self.rand = None

    def _play_card(self, card: Card):
        self.game.play_card(card)

    def _play_until_agent_turn(self):
        while not self.game.done and self.game.current_player != self.player_id:
            player = self.other_players[self.game.current_player]
            self._play_card(player.next_card(self.game.current_hand, self.game.current_valid_cards))

    def reset(self, seed=None):
        if seed is not None:
            self.rand = Random(seed)
        else:
            self.rand = self.rand or Random(os.urandom(128))

        self.game = SkatGame(self.rand, self.rand.randint(0, 2))
        for player_id, player in enumerate(self.other_players):
            for observer in player.observers:
                self.game.add_observer(observer, player_id)
        self.game.add_observer(self.observer, self.player_id)

        if self.position == PlayerPosition.after_soloist:
            soloist = SkatGame.prev_player(self.player_id)
        elif self.position == PlayerPosition.before_soloist:
            soloist = SkatGame.next_player(self.player_id)
        else:
            soloist = self.player_id
        solo_hand = self.game.hands[soloist]
        trump, skat = self.trump_strategy.choose_trump_and_skat(solo_hand, self.game.skat) \
            if self.party == PlayerParty.soloist \
            else self.other_players[soloist].choose_trump_and_skat(solo_hand, self.game.skat)

        self.game.set_bid_results(trump, soloist, skat)
        self._play_until_agent_turn()
        return self.observer.get_observation()

    def step(self, action: int):
        card = self.observer.get_card(action)
        self._play_card(card)
        self._play_until_agent_turn()
        reward = self.observer.get_reward()
        return self.observer.get_observation(), reward, self.game.done, {}

    def action_masks(self):
        valid_cards = self.game.current_valid_cards
        return np.array([self.observer.get_card(action) in valid_cards for action in range(32)])

    def render(self, mode="ansi"):
        if mode == "ansi":
            return "\n".join([
                f"player 1: {self.game.hands[0]}",
                f"player 2: {self.game.hands[1]}",
                f"player 3 (agent): {self.game.hands[2]}",
                f"stich: {self.game.current_stich}",
                f"player_points: {self.game.points[self.party]}"
            ])
        else:
            super().render(mode=mode)
