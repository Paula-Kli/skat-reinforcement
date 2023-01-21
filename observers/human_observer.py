from card import Card, Suit
from .observer import Observer


class HumanObserver(Observer):
    def __init__(self):
        super().__init__()
        self.id = None
        self.soloist = None

    def on_game_start(self, player_id: int, hand: list[Card]):
        self.id = player_id
        print("==== Starting new game ====")
        print(f"You are player {player_id}.")
        print(f"Your initial cards: {', '.join(str(card) for card in hand)}")

    def on_trump(self, trump: Suit):
        print(f"{trump} is trump")

    def on_soloist(self, soloist: int):
        self.soloist = soloist
        if soloist == self.id:
            print("You play as soloist.")
        else:
            print(f"Player {soloist} plays as soloist.")

    def on_skat(self, skat: list[Card], new_hand: list[Card]):
        print(f"You pushed {' and '.join(str(card) for card in skat)} to skat.")

    def _player_name(self, player_id: int):
        if player_id == self.id:
            return "You"
        name = f"Player {player_id}"
        if self.id != self.soloist:
            name += f" ({'soloist' if player_id == self.soloist else 'partner'})"
        return name

    def on_card_played(self, card: Card, player_id: int):
        print(f"{self._player_name(player_id)} played {card}.")

    def on_stich_made(self, winner: int, points: int):
        print(f"----- {self._player_name(winner)} made the stich - {points} points. -----")