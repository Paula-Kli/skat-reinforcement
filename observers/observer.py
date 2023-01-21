from card import Card, Suit


class Observer:
    def __str__(self):
        return self.__class__.__name__

    def on_game_start(self, player_id: int, hand: list[Card]):
        pass

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        pass

    def on_trump(self, trump: Suit):
        pass

    def on_soloist(self, soloist: int):
        pass

    def on_card_played(self, card: Card, player: int):
        pass

    def on_stich_made(self, winner: int, points: int):
        pass
