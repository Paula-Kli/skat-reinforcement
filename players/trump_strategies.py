from random import Random
from typing import Optional

from card import Suit, Card, Rank


class TrumpStrategy:
    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        raise NotImplementedError


class RandomTrumpStrategy(TrumpStrategy):
    def __init__(self, seed: Optional[int]):
        self.random_generator = Random(seed)

    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        return self.random_generator.choice(list(Suit)), skat


class FixedTrumpStrategy(TrumpStrategy):
    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        return Suit.spade, skat


class SuitAmountTrumpStrategy(TrumpStrategy):
    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        combined = skat + hand
        amount = [0, 0, 0, 0]
        for card in combined:
            if card.rank != Rank.jack:
                amount[card.suit] += 1
        suit = Suit(amount.index(max(amount)))

        new_skat = []

        for i in range(2):
            min_card = min([c for c in combined if c.suit != suit and c.rank != Rank.jack], key=lambda c: c.reward)
            new_skat.append(min_card)
            combined.remove(min_card)

        return suit, new_skat


class SuitAmountTrumpStrategyBetterSkat(TrumpStrategy):
    def choose_trump_and_skat(self, hand: list[Card], skat: list[Card]) -> tuple[Suit, list[Card]]:
        combined = skat + hand
        amount = [0, 0, 0, 0]
        for card in combined:
            if card.rank != Rank.jack:
                amount[card.suit] += 1
            else:
                combined.remove(card)
        suit = Suit(amount.index(max(amount)))

        new_skat = []

        cards_ordering = [[card for card in combined if card.suit == suit and card.rank != Rank.ace] for suit in Suit]
        cards_ordering = sorted(cards_ordering, key=lambda cards: len(cards))

        for cards_list in cards_ordering:
            if len(cards_list) == 0:
                continue
            cards_list = sorted(cards_list, key=lambda card: card.reward)
            for card in reversed(cards_list):
                if len(new_skat) < 2:
                    new_skat.append(card)

        return suit, new_skat
