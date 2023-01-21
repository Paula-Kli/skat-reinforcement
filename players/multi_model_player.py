import os
from typing import Optional

import numpy as np
from stable_baselines3.common.base_class import BaseAlgorithm

from card import Card
from observers import Observer
from skat_env import PlayerPosition
from skat_game import SkatGame
from training import configs
from training.utility import find_latest_model
from .player import Player


class MultiModelPlayer(Player, Observer):
    def __init__(self, folder: str, device="auto", *args, **kwargs):
        """
        Creates a player from the latest versions of self-trained models
        :param path: The path to the folder containing sub-folders for each position, relative to the root folder.
        This also determines the config.
        """
        super().__init__(*args, **kwargs)
        subfolders = os.listdir(folder)
        for pos in PlayerPosition:
            assert pos.name in subfolders
        config_name, env_settings = folder.split("/")[-2:]
        self.config = configs.get(config_name)
        self.folder = folder
        self.device = device
        # lazy init for model loading
        self.models: list[Optional[BaseAlgorithm]] = [None for pos in PlayerPosition]
        self.id: Optional[int] = None
        self.position: Optional[PlayerPosition] = None
        self.name = self.name or f"{config_name}_{env_settings}"
        self.model_observer = self.config.observer(**self.config.observer_kwargs)
        self.observers.append(self.model_observer)
        self.trump_strategy = self.config.trump_strategy()
        self.kwargs.update(folder=folder, device=device)

    def on_game_start(self, player_id: int, hand: list[Card]):
        self.id = player_id

    def on_soloist(self, soloist: int):
        if self.id == SkatGame.prev_player(soloist):
            self.position = PlayerPosition.before_soloist
        elif self.id == SkatGame.next_player(soloist):
            self.position = PlayerPosition.after_soloist
        else:
            self.position = PlayerPosition.soloist

    def _action_masks(self, valid_cards: list[Card]):
        return np.array([self.model_observer.get_card(action) in valid_cards for action in range(32)])

    def get_model(self):
        if self.models[self.position] is None:
            model_path, _ = find_latest_model(f"{self.folder}/{self.position.name}")
            self.models[self.position] = self.config.algorithm.load(
                model_path, policy_kwargs=self.config.policy_kwargs, device=self.device)
        return self.models[self.position]

    def next_card(self, hand: list[Card], valid_cards: list[Card]):
        action, _ = self.get_model().predict(
            self.model_observer.get_observation(), deterministic=True, action_masks=self._action_masks(valid_cards))
        return self.model_observer.get_card(int(action))
