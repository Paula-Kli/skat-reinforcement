from itertools import chain
from typing import Optional

from card import Card, Suit, Rank, CardInfo, IngameSuit
from observers import Observer
from players import Player
from players.trump_strategies import SuitAmountTrumpStrategyBetterSkat
from skat_game import Stich


class CardPositions:
    @staticmethod
    def index(player: int, card: Card):
        return card.suit * len(Rank) * 3 + card.rank * 3 + player

    def __init__(self, own_id: int, hand: list[Card]):
        self.card_info: Optional[CardInfo] = None

        # initially any card could be anywhere
        self.positions = [True] * len(Suit) * len(Rank) * 3
        # initialize positions with knowledge of own hand cards
        for card in Card.all():
            self.set_player_has_card_not(own_id, card)
        for card in hand:
            self.set_player_has_card(own_id, card)

    def set_card_info(self, card_info: CardInfo):
        self.card_info = card_info

    def player_has_card(self, player: int, card: Card):
        return self.positions[self.index(player, card)]

    def player_has_card_prob(self, player: int, card: Card) -> float:
        return 0 if not self.player_has_card(player, card) else 1 / sum(self.player_has_card(p, card) for p in range(3))

    def set_player_has_card(self, player: int, card: Card):
        for p in range(3):
            self.positions[self.index(p, card)] = p == player

    def set_player_has_card_not(self, player: int, card: Card):
        self.positions[self.index(player, card)] = False

    def set_played(self, card: Card):
        for p in range(3):
            self.set_player_has_card_not(p, card)

    def player_has_suit(self, player: int, suit: IngameSuit):
        return any(self.player_has_card(player, card) for card in self.card_info.cards(suit))

    def player_has_suit_prob(self, player: int, suit: IngameSuit) -> float:
        p_player_has_suit_not = 1
        for card in self.card_info.cards(suit):
            p_player_has_suit_not *= 1 - self.player_has_card_prob(player, card)
        return 1 - p_player_has_suit_not

    def highest_unplayed_card(self, suit: IngameSuit):
        for card in reversed(self.card_info.cards(suit)):
            if any(self.player_has_card(p, card) for p in range(3)):
                return card
        return None

    def highest_card(self, player: int, suit: IngameSuit):
        for card in reversed(self.card_info.cards(suit)):
            if self.player_has_card(player, card):
                return card
        return None

    def player_wins_prob(self, player: int, against_card: Card, leading_suit: IngameSuit) -> float:
        against_strength = self.card_info.ingame_strength(against_card, leading_suit)
        no_higher_in_suit = 1
        for card in filter(
            lambda c: self.card_info.ingame_strength(c, leading_suit) > against_strength,
            self.card_info.cards(self.card_info.ingame_suit(against_card))
        ):
            no_higher_in_suit *= 1 - self.player_has_card_prob(player, card)

        if leading_suit == IngameSuit.trump:
            return 1 - no_higher_in_suit
        else:
            player_has_suit_not = 1 - self.player_has_suit_prob(player, leading_suit)
            player_has_trump = self.player_has_suit_prob(player, IngameSuit.trump)
            return (1 - no_higher_in_suit) + player_has_suit_not * player_has_trump


class AdvancedPlayer(Player, Observer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trump_strategy = self.trump_strategy or SuitAmountTrumpStrategyBetterSkat()
        self.card_info: Optional[CardInfo] = None
        self.card_positions: Optional[CardPositions] = None
        self.id: Optional[int] = None
        self.soloist: Optional[int] = None
        self.partner: Optional[int] = None
        self.current_stich: Optional[Stich] = None
        self.leading_suit: Optional[IngameSuit] = None

    # --- observer methods ---

    def on_game_start(self, player: int, hand: list[Card]):
        self.card_positions = CardPositions(player, hand)
        self.current_stich = []
        self.id = player

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        for card in new_hand:
            self.card_positions.set_player_has_card(self.id, card)
        for card in skat:
            self.card_positions.set_played(card)

    def on_soloist(self, soloist: int):
        self.soloist = soloist
        self.partner = None if self.id == soloist else 3 - self.id - soloist

    def on_trump(self, trump: Suit):
        self.card_info = CardInfo(trump)
        self.card_positions.set_card_info(self.card_info)

    def on_card_played(self, card: Card, player: int):
        self.card_positions.set_played(card)
        self.current_stich.append((card, player))
        ingame_suit = self.card_info.ingame_suit(card)
        if self.leading_suit is None:
            self.leading_suit = ingame_suit
        if ingame_suit != self.leading_suit:
            for card in self.card_info.cards(self.leading_suit):
                self.card_positions.set_player_has_card_not(player, card)

    def on_stich_made(self, winner: int, points: int):
        self.current_stich.clear()
        self.leading_suit = None

    # --- playing logic

    def is_opponent(self, player: int):
        return player != self.id and player != self.partner

    def safe_trump(self):
        highest = self.card_positions.highest_unplayed_card(IngameSuit.trump)
        if highest and self.card_positions.player_has_card(self.id, highest):
            return highest

    def draw_trump(self):
        for card in chain(reversed(self.card_info.jacks()), self.card_info.non_jacks(IngameSuit.trump)):
            if self.card_positions.player_has_card(self.id, card):
                return card

    def safe_non_trump_solo(self):
        if all(not self.card_positions.player_has_suit(p, IngameSuit.trump) for p in range(3) if p != self.id):
            for suit in self.card_info.non_trump_suits():
                highest = self.card_positions.highest_unplayed_card(suit)
                if highest and self.card_positions.player_has_card(self.id, highest):
                    return highest

    def cheap_non_trump(self, cards: list[Card]):
        return min((card for card in cards if not self.card_info.is_trump(card)), key=CardInfo.reward)

    def played_card(self, player: int) -> Optional[Card]:
        return next((card for card, p in self.current_stich if p == player), None)

    def played_opponent_cards(self):
        return [card for card, player in self.current_stich if self.is_opponent(player)]

    def likely_highest_card(self, player):
        trump_card = None
        if self.card_positions.player_has_suit_prob(player, self.leading_suit) < 0.75:
            trump_card = self.card_positions.highest_card(player, IngameSuit.trump)
        return trump_card or self.card_positions.highest_card(player, self.leading_suit)

    def possible_opponent_cards(self):
        return [self.likely_highest_card(p) for p in range(3) if self.is_opponent(p) and self.played_card(p) is None]

    def assumed_opponent_cards(self):
        return self.played_opponent_cards() + self.possible_opponent_cards()

    def wins_against(self, card1: Card, card2: Card):
        return max(card1, card2, key=lambda card: self.card_info.ingame_strength(card, self.leading_suit)) is card1

    def winning_cards(self, cards: list[Card], opponent_cards: list[Card]):
        return [card for card in cards if all(self.wins_against(card, op_card) for op_card in opponent_cards)]

    def follow_suit_safe(self, cards: list[Card]):
        safe_winning_cards = self.winning_cards(cards, self.assumed_opponent_cards())
        if safe_winning_cards:
            return max(safe_winning_cards, key=CardInfo.reward)

    def follow_suit_contest(self, cards: list[Card]):
        contesting_cards = self.winning_cards(cards, self.played_opponent_cards())
        cheap_contesting = [card for card in contesting_cards if card.reward <= 4]
        if cheap_contesting:
            return min(cheap_contesting, key=CardInfo.reward)

    def weak_card(self, cards: list[Card]):
        return min(cards, key=lambda c: self.card_info.ingame_strength(c, self.leading_suit))

    def safe_non_trump_defender(self, solo_suit_probs: list[tuple[IngameSuit, float]]):
        for suit, solo_suit_prob in solo_suit_probs:
            if solo_suit_prob < 0.8:
                continue
            highest = self.card_positions.highest_unplayed_card(suit)
            if self.card_positions.player_has_card(self.id, highest):
                return highest

    def feed_stich(self, solo_suit_probs: list[tuple[IngameSuit, float]]):
        # play suit which soloist likely/unlikely has if partner/soloist sits after me
        partner_after_me = self.partner == (self.id + 1) % 3
        for suit, solo_suit_prob in solo_suit_probs if partner_after_me else reversed(solo_suit_probs):
            for rank in (Rank.king, Rank.queen, Rank.nine, Rank.eight, Rank.seven):
                card = Card(Suit(suit), rank)
                if self.card_positions.player_has_card(self.id, card):
                    return card

    def play_team(self, cards: list[Card]):
        partner_card = self.played_card(self.partner)
        soloist_card = self.played_card(self.soloist)
        # play high reward card if partner wins
        if partner_card and soloist_card:
            if self.wins_against(partner_card, soloist_card):
                return max(cards, key=CardInfo.reward)
        # play high reward card if partner is likely to take stich
        elif not partner_card and soloist_card:
            if self.card_positions.player_wins_prob(self.partner, soloist_card, self.leading_suit) >= 0.8:
                return max(cards, key=CardInfo.reward)
        # play high reward card if soloist is unlikely to get stich
        elif partner_card and not soloist_card:
            if self.card_positions.player_wins_prob(self.soloist, partner_card, self.leading_suit) < 0.2:
                return max(cards, key=CardInfo.reward)

    def next_card(self, hand: list[Card], valid_cards: list[Card]) -> Card:
        if self.id == self.soloist:
            if self.leading_suit is None:
                return self.safe_trump() or self.draw_trump() or self.safe_non_trump_solo() \
                       or self.cheap_non_trump(valid_cards)
            else:
                return self.follow_suit_safe(valid_cards) or self.follow_suit_contest(valid_cards) \
                       or self.weak_card(valid_cards)
        else:
            if self.leading_suit is None:
                # determine which (non-trump) suits solo player is most likely to have (high probability first)
                solo_suit_probs = [
                    (suit, self.card_positions.player_has_suit_prob(self.soloist, suit))
                    for suit in self.card_info.non_trump_suits()
                ]
                solo_suit_probs.sort(key=lambda suit_prob: suit_prob[1], reverse=True)
                return self.safe_non_trump_defender(solo_suit_probs) or self.feed_stich(solo_suit_probs) \
                    or self.safe_trump() or self.weak_card(valid_cards)
            else:
                return self.play_team(valid_cards) or self.follow_suit_safe(valid_cards) or self.weak_card(valid_cards)
