from typing import Optional

from card import Card, Suit
from observers import Observer
from players.trump_strategies import RandomTrumpStrategy, TrumpStrategy


class Player:
    def __init__(
        self, name: Optional[str] = None, trump_strategy: TrumpStrategy = None, seed: Optional[int] = None,
        **kwargs
    ):
        self.name = name
        self.seed = seed
        self.trump_strategy = trump_strategy
        self.kwargs = dict(name=name, trump_strategy=trump_strategy, seed=seed)
        self.observers = [self] if isinstance(self, Observer) else []

    def __str__(self):
        return self.name or self.__class__.__name__

    def next_card(self, hand: list[Card], valid_cards: list[Card]) -> Card:
        raise NotImplementedError

    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        return self.trump_strategy.choose_trump_and_skat(hand, skat)

    def clone(self):
        return self.__class__(**self.kwargs)
