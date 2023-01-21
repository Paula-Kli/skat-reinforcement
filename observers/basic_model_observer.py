from typing import Optional

from gym.spaces import Discrete

from card import Card, Suit, Rank
from observers import ModelObserver


class CardMapping:
    def __init__(self, card_order: list[Card]):
        self.cards = card_order
        self.card_ids = {card: card_id for card_id, card in enumerate(self.cards)}

    def id(self, card: Card):
        return self.card_ids[card]

    def card(self, card_id: int):
        return self.cards[card_id]


def simple_card_mapping(trump: Suit):
    return CardMapping([Card(suit, rank) for suit in Suit for rank in Rank])


def positional_trump_mapping(trump: Suit):
    cards: list[Card] = []
    for suit in Suit:
        cards.append(Card(suit, Rank.jack))
    for rank in Rank:
        if rank != Rank.jack:
            cards.append(Card(trump, rank))
    for suit in Suit:
        if suit == trump:
            continue
        for rank in Rank:
            if rank != Rank.jack:
                cards.append(Card(suit, rank))
    return CardMapping(cards)


class BasicModelObserver(ModelObserver):
    def __init__(self, positional_trump=False, win_reward=False):
        super().__init__()
        self._positional_trump = positional_trump
        self._win_reward = win_reward
        self._card_mapping_generator = positional_trump_mapping if positional_trump else simple_card_mapping
        self._card_mapping = None

        # agent can play a single card
        self.action_space = Discrete(32)

        self._total_points: Optional[int] = None
        self._last_points: Optional[int] = None
        self._id: Optional[int] = None
        self._soloist: Optional[int] = None
        self._trump: Optional[Suit] = None
        self._round: Optional[int] = None
        self._initial_hand: Optional[list[Card]] = None

    def on_game_start(self, player_id: int, hand: list[Card]):
        self._id = player_id
        self._initial_hand = hand
        self._round = 0
        self._total_points = 0
        self._last_points = 0

    def on_trump(self, trump: Suit):
        self._card_mapping = self._card_mapping_generator(trump)
        self._trump = trump

    def on_soloist(self, soloist: int):
        self._soloist = soloist

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        for card in skat:
            self._total_points += card.reward

    def on_stich_made(self, winner: int, points: int):
        self._round += 1
        win_as_soloist = self._soloist == self._id and winner == self._soloist
        win_as_defender = self._soloist != self._id and winner != self._soloist
        win = win_as_soloist or win_as_defender
        self._total_points += points if win else 0
        self._last_points = points if win else 0

    def get_observation(self):
        raise NotImplementedError

    def get_reward(self):
        reward = self._last_points
        if self._win_reward and self._round == 10:
            if self._total_points == 120:
                reward += 120
            if self._total_points > 90:
                reward += 90
            elif self._total_points > 60:
                reward += 60
            elif self._total_points >= 30:
                reward -= 30
            elif self._total_points >= 1:
                reward -= 60
            else:
                reward -= 120
        return reward

    def get_card(self, action: int):
        return self._card_mapping.card(action)
