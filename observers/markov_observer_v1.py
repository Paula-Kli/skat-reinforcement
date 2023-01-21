from enum import IntEnum
from typing import Optional

import numpy as np
from gym.spaces import Discrete, Dict, MultiDiscrete, Box

from card import Card, Suit
from skat_game import SkatGame
from .basic_model_observer import BasicModelObserver


class CardPosition(IntEnum):
    agent_hand = 0
    other_player_hand = 1
    played = 2


class MarkovObserverV1(BasicModelObserver):
    def __init__(self, positional_trump=False, win_reward=False):
        super().__init__(positional_trump=positional_trump, win_reward=win_reward)

        # observation includes current card positions, stich history and further features
        self.observation_space = Dict({
            "card_positions": MultiDiscrete([len(CardPosition)] * 32),
            **({} if positional_trump else {"trump": Discrete(len(Suit))}),
            # each card (3) in each stich (10) can have 32 values * 3 possible players + "no card played" possibility
            "stich_list": MultiDiscrete([3 * 32 + 1] * (3 * 10)),
            "total_points": Box(0, 120, shape=(1,), dtype=int)
        })

        self._card_positions: Optional[np.ndarray] = None
        self._stich_array: Optional[np.ndarray] = None
        self._stich_window: Optional[tuple[int, int]] = None
        self._current_card_index: Optional[int] = None

    def _set_card_position(self, card: Card, position: CardPosition):
        self._card_positions[self._card_mapping.id(card)] = position

    def _card_event_id(self, card: Optional[Card], player_id: Optional[int]):
        if card is None:
            return 96
        relative_player_pos = (self._id - player_id) % 3
        return relative_player_pos * 32 + self._card_mapping.id(card)

    def _init_observation_state(self):
        # use sliding window to keep current stich at end of window
        self._stich_array = np.full(60, self._card_event_id(None, None))
        self._stich_window = (0, 30)
        self._current_card_index = 27
        self._card_positions = np.full(32, CardPosition.other_player_hand)
        for card in self._initial_hand:
            self._set_card_position(card, CardPosition.agent_hand)

    def on_trump(self, trump: Suit):
        super().on_trump(trump)
        self._init_observation_state()

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        super().on_skat(skat, new_hand)
        for card in skat:
            self._set_card_position(card, CardPosition.played)

    def on_card_played(self, card: Card, player_id: int):
        super().on_card_played(card, player_id)
        self._set_card_position(card, CardPosition.played)
        self._stich_array[self._current_card_index] = self._card_event_id(card, player_id)
        self._current_card_index += 1

    def _stich_list(self):
        begin, end = self._stich_window
        return self._stich_array[begin:end]

    def get_observation(self):
        return {
            "card_positions": self._card_positions,
            **({} if self._positional_trump else {"trump": self._trump}),
            "stich_list": self._stich_list(),
            "total_points": np.array([self._total_points])
        }
