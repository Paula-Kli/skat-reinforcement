from operator import attrgetter

from card import Card, Suit, Rank
from observers import Observer
from .player import Player


# A simple opponent who plays highest card possible
from .trump_strategies import SuitAmountTrumpStrategyBetterSkat


class SimplePlayerV1(Player, Observer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trump_strategy = self.trump_strategy or SuitAmountTrumpStrategyBetterSkat()
        self.current_stich: list[Card] = []
        self.ace_played = [False for suit in Suit]

    def on_game_start(self, player_id: int, hand: list[Card]):
        self.current_stich = []
        self.ace_played = [False for suit in Suit]

    def on_stich_made(self, winner: int, points: int):
        self.current_stich = []

    def on_card_played(self, card: Card, player: int):
        self.current_stich.append(card)
        if card.rank == Rank.ace:
            self.ace_played[card.suit] = True

    def next_card(self, hand: list[Card], valid_cards: list[Card]):
        valid_cards = valid_cards
        if not self.current_stich:
            card = max(valid_cards, key=attrgetter('reward'))
            if not self.ace_played[card.suit] and card.rank != Rank.ace:
                card = min(valid_cards, key=attrgetter('reward'))
        elif any(self.current_stich[0].suit == c.suit for c in valid_cards):
            matching_suit = [card for card in valid_cards if card.suit == self.current_stich[0].suit]
            if not matching_suit:
                # there is a card with a higher value in my hand with matching suit
                card = max(matching_suit, key=attrgetter('reward'))
            else:
                card = min(matching_suit, key=attrgetter('reward'))
        else:
            card = min(valid_cards, key=attrgetter('reward'))
        return card
