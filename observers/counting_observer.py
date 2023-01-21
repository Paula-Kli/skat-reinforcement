from enum import IntEnum
from typing import Optional

import numpy as np
from gym.spaces import Discrete, Dict, MultiDiscrete, Box, MultiBinary

from card import Card, Suit, IngameSuit, CardInfo
from skat_game import Stich
from .basic_model_observer import BasicModelObserver


class CountingObserver(BasicModelObserver):
    def __init__(self, positional_trump=False, win_reward=False):
        super().__init__(positional_trump=positional_trump, win_reward=win_reward)

        # observation includes current card positions, stich history and further features
        self.observation_space = Dict({
            # for each card and player, states if the player could have the card
            "card_options": MultiBinary(32*3),
            # each card from other player (2) can have 32 values * 2 possible players + "no card played" possibility
            "stich": MultiDiscrete((65, 65)),
            **({} if positional_trump else {"trump": Discrete(len(Suit))}),
            "total_points": Box(0, 120, shape=(1,), dtype=int)
        })

        self._card_options: Optional[np.ndarray] = None
        self._card_info: Optional[CardInfo] = None
        self._current_stich: Stich = []
        self.leading_suit: Optional[IngameSuit] = None

    def relative_id(self, player_id):
        return (player_id - self._id) % 3

    def _set_player_has(self, card: Card, player: int):
        player = self.relative_id(player)
        self._card_options[self._card_mapping.id(card)] = [p == player for p in range(3)]

    def _set_player_has_not(self, card: Card, player: int):
        player = self.relative_id(player)
        self._card_options[self._card_mapping.id(card), player] = False

    def _set_played(self, card: Card):
        self._card_options[self._card_mapping.id(card)] = [False, False, False]

    def _init_observation_state(self):
        # initially each card is expected to be on other player hand
        self._card_options = np.array([[p != self._id for p in range(3)]] * 32)
        # except for those in the own hand
        for card in self._initial_hand:
            self._set_player_has(card, self._id)

    def on_game_start(self, player_id: int, hand: list[Card]):
        super().on_game_start(player_id, hand)
        self._current_stich.clear()
        self.leading_suit = None

    def on_trump(self, trump: Suit):
        super().on_trump(trump)
        self._init_observation_state()
        self._card_info = CardInfo(trump)

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        super().on_skat(skat, new_hand)
        for card in new_hand:
            self._set_player_has(card, self._id)
        for card in skat:
            self._set_played(card)

    def on_card_played(self, card: Card, player_id: int):
        super().on_card_played(card, player_id)
        self._set_played(card)
        self._current_stich.append((card, player_id))
        ingame_suit = self._card_info.ingame_suit(card)
        if self.leading_suit is None:
            self.leading_suit = ingame_suit
        elif ingame_suit != self.leading_suit:
            for card in self._card_info.cards(self.leading_suit):
                self._set_player_has_not(card, player_id)

    def on_stich_made(self, winner: int, points: int):
        super().on_stich_made(winner, points)
        self._current_stich.clear()
        self.leading_suit = None

    def _card_event_id(self, card: Optional[Card], player_id: Optional[int]):
        if card is None:
            return 64
        # subtract 1 because player_id is never self.id
        return (self.relative_id(player_id) - 1) * 32 + self._card_mapping.id(card)

    def get_observation(self):
        stich = [self._card_event_id(card, card_id) for card, card_id in self._current_stich]
        stich += [self._card_event_id(None, None)] * (2 - len(stich))
        return {
            "card_options": np.reshape(self._card_options, 32*3),
            "stich": np.array(stich),
            **({} if self._positional_trump else {"trump": self._trump}),
            "total_points": np.array([self._total_points])
        }
