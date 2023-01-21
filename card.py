from enum import IntEnum
from typing import Optional


class Suit(IntEnum):
    def __str__(self):
        return ['♦', '♥', '♠', '♣'][self.value]

    diamond = 0
    heart = 1
    spade = 2
    club = 3


class IngameSuit(IntEnum):
    diamond = 0
    heart = 1
    spade = 2
    club = 3
    trump = 4


class Rank(IntEnum):
    def __str__(self):
        return ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'][self.value]

    seven = 0
    eight = 1
    nine = 2
    ten = 3
    jack = 4
    queen = 5
    king = 6
    ace = 7


class Card:
    _rewards = [0, 0, 0, 10, 2, 3, 4, 11]

    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.reward = self._rewards[rank]

    def __repr__(self):
        return f"{self.suit} {self.rank}"

    def __hash__(self):
        return self.suit * len(Rank) + self.rank

    def __eq__(self, other: "Card"):
        return self.suit == other.suit and self.rank == other.rank

    @staticmethod
    def all():
        return (Card(suit, rank) for suit in Suit for rank in Rank)

    @staticmethod
    def get_reward(card: "Card"):
        return card.reward


class CardInfo:
    _ranks_by_strength = (Rank.seven, Rank.eight, Rank.nine, Rank.queen, Rank.king, Rank.ten, Rank.ace)
    _strengths_by_rank = (0, 1, 2, 5, None, 3, 4, 6)

    @staticmethod
    def reward(card: Card):
        return card.reward

    @classmethod
    def strength(cls, card: Card) -> int:
        return 7 + card.suit if card.rank == Rank.jack else cls._strengths_by_rank[card.rank]

    def __init__(self, trump: Suit):
        self.trump = trump

    @staticmethod
    def jacks():
        """:returns: The jacks in ascending strength."""
        return [Card(suit, Rank.jack) for suit in Suit]

    def non_jacks(self, ingame_suit: IngameSuit) -> list[Card]:
        """:returns: The non-jack cards of the given suit in ascending strength."""
        suit = self.suit(ingame_suit)
        return [Card(suit, rank) for rank in self._ranks_by_strength] if suit is not None else []

    def cards(self, ingame_suit: IngameSuit):
        """:returns: The cards of the given suit, sorted by ascending strength."""
        cards = self.non_jacks(ingame_suit)
        if ingame_suit == self.trump or ingame_suit == IngameSuit.trump:
            cards.extend(self.jacks())
        return cards

    def is_trump(self, card: Card):
        return card.rank == Rank.jack or card.suit == self.trump

    def ingame_suit(self, card: Card) -> IngameSuit:
        return IngameSuit.trump if self.is_trump(card) else card.suit

    def suit(self, ingame_suit: IngameSuit) -> Optional[Suit]:
        return self.trump if ingame_suit == IngameSuit.trump else Suit(ingame_suit)

    def non_trump_suits(self):
        return [suit for suit in IngameSuit if suit != self.trump and suit != IngameSuit.trump]

    def ingame_strength(self, card: Optional[Card], leading_suit: IngameSuit):
        if card is None:
            return -1
        strength = self.strength(card)
        ingame_suit = self.ingame_suit(card)
        if ingame_suit == IngameSuit.trump:
            strength += 14
        elif ingame_suit == leading_suit:
            strength += 7
        return strength
