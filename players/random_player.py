import random

from card import Card
from .player import Player
from .trump_strategies import RandomTrumpStrategy


class RandomPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_generator = random.Random(self.seed)
        self.trump_strategy = self.trump_strategy or RandomTrumpStrategy(self.seed)

    def next_card(self, hand: list[Card], valid_cards: list[Card]):
        return self.random_generator.choice(valid_cards)
