from enum import IntEnum
from random import Random
from typing import Optional

from card import Card, Suit, CardInfo
from observers import Observer

Stich = list[tuple[Card, int]]


class PlayerParty(IntEnum):
    soloist = 0
    defenders = 1


class SkatGame:
    @staticmethod
    def next_player(player: int):
        return (player + 1) % 3

    @staticmethod
    def prev_player(player: int):
        return (player + 2) % 3

    def __init__(self, rand_gen=Random(), start_player=0):
        super().__init__()
        self.cards = list(Card.all())
        rand_gen.shuffle(self.cards)
        self.hands = [self.cards[0:10], self.cards[10:20], self.cards[20:30]]
        self.skat = self.cards[30:32]
        self.card_info: Optional[CardInfo] = None

        self.points = [0, 0]
        self.soloist: Optional[int] = None
        self.player_parties: Optional[list[PlayerParty]] = None

        self.stich_list: list[Stich] = [[]]
        self.start_player = start_player
        self.current_player = start_player

        self._observers: list[tuple[Observer, int]] = []

    def add_observer(self, observer: Observer, player_id: int):
        self._observers.append((observer, player_id))
        observer.on_game_start(player_id, self.hands[player_id])

    def set_bid_results(self, trump: Suit, soloist: int, skat: list[Card]):
        self.card_info = CardInfo(trump)
        self.soloist = soloist
        self.player_parties = [PlayerParty.soloist if i == soloist else PlayerParty.defenders for i in range(3)]
        self._set_skat(skat)
        self.points[PlayerParty.soloist] += sum(card.reward for card in self.skat)
        for observer, player_id in self._observers:
            observer.on_trump(trump)
            observer.on_soloist(soloist)
            if player_id == soloist:
                observer.on_skat(self.skat, self.hands[self.soloist])

    def _set_skat(self, skat: list[Card]):
        hand_solo = self.hands[self.soloist] + self.skat
        assert all(card in hand_solo for card in skat)
        for card in skat:
            hand_solo.remove(card)
        self.hands[self.soloist] = hand_solo
        self.skat = skat

    @property
    def done(self):
        return len(self.stich_list) > 10

    @property
    def current_hand(self):
        return self.hands[self.current_player]

    @property
    def current_stich(self):
        return self.stich_list[-1]

    def follows_suit(self, card: Card):
        if len(self.current_stich) == 0:
            return True
        return self.card_info.ingame_suit(self.current_stich[0][0]) == self.card_info.ingame_suit(card)

    @property
    def current_valid_cards(self) -> list[Card]:
        suit_following_cards = [card for card in self.current_hand if self.follows_suit(card)]
        return suit_following_cards or self.current_hand

    def winner(self, stich: Stich) -> int:
        assert len(stich) == 3
        leading_suit = self.card_info.ingame_suit(stich[0][0])
        return max(stich, key=lambda card_player: self.card_info.ingame_strength(card_player[0], leading_suit))[1]

    def play_card(self, card: Card):
        if self.done:
            raise RuntimeError("Game is already over")
        elif card not in self.current_valid_cards:
            raise ValueError(f"Card {card} is not valid")
        else:
            self.current_hand.remove(card)
            self.current_stich.append((card, self.current_player))
            for observer, _ in self._observers:
                observer.on_card_played(card, self.current_player)
            if len(self.current_stich) == 3:
                winner = self.winner(self.current_stich)
                stich_value = sum(c.reward for c, _ in self.current_stich)
                for observer, _ in self._observers:
                    observer.on_stich_made(winner, stich_value)
                self.points[self.player_parties[winner]] += stich_value
                self.stich_list.append([])
                self.current_player = winner
            else:
                self.current_player = self.next_player(self.current_player)

    def winning_party(self):
        if not self.done:
            return None
        return PlayerParty.soloist if self.points[PlayerParty.soloist] > 60 else PlayerParty.defenders
