from enum import IntEnum
from typing import Optional

import numpy as np
from gym.spaces import Discrete, Dict, MultiDiscrete, Box

from card import Card, Suit
from skat_game import Stich
from .basic_model_observer import BasicModelObserver


class CardPosition(IntEnum):
    agent_hand = 0
    other_player_hand = 1
    played = 2


class DrunkenRainerObserverV2(BasicModelObserver):
    def __init__(self, positional_trump=False, win_reward=False):
        super().__init__(positional_trump=positional_trump, win_reward=win_reward)

        # observation includes current card positions, stich history and further features
        self.observation_space = Dict({
            "card_positions": MultiDiscrete([len(CardPosition)] * 32),
            # each card from other player (2) can have 32 values * 2 possible players + "no card played" possibility
            "stich": MultiDiscrete([65, 65]),
            **({} if positional_trump else {"trump": Discrete(len(Suit))}),
            "total_points": Box(0, 120, shape=(1,), dtype=int)
        })

        self._card_positions: Optional[np.ndarray] = None
        self._current_stich: Stich = []

    def _set_card_position(self, card: Card, position: CardPosition):
        self._card_positions[self._card_mapping.id(card)] = position

    def _init_observation_state(self):
        self._card_positions = np.full(32, CardPosition.other_player_hand)
        for card in self._initial_hand:
            self._set_card_position(card, CardPosition.agent_hand)

    def on_trump(self, trump: Suit):
        super().on_trump(trump)
        self._init_observation_state()

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        super().on_skat(skat, new_hand)
        for card in new_hand:
            self._set_card_position(card, CardPosition.agent_hand)
        for card in skat:
            self._set_card_position(card, CardPosition.played)

    def on_card_played(self, card: Card, player_id: int):
        super().on_card_played(card, player_id)
        self._set_card_position(card, CardPosition.played)
        self._current_stich.append((card, player_id))

    def on_stich_made(self, winner: int, points: int):
        super().on_stich_made(winner, points)
        self._current_stich = []

    def _card_event_id(self, card: Optional[Card], player_id: Optional[int]):
        if card is None:
            return 64
        # subtract 1 because player_id is never self.id
        relative_player_pos = (self._id - player_id - 1) % 3
        return relative_player_pos * 32 + self._card_mapping.id(card)

    def get_observation(self):
        stich = [self._card_event_id(card, card_id) for card, card_id in self._current_stich]
        stich += [self._card_event_id(None, None)] * (2 - len(stich))
        return {
            "card_positions": self._card_positions,
            "stich": np.array(stich),
            **({} if self._positional_trump else {"trump": self._trump}),
            "total_points": np.array([self._total_points])
        }
