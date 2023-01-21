from card import Card
from observers import HumanObserver
from .player import Player
from .trump_strategies import SuitAmountTrumpStrategyBetterSkat


class HumanPlayer(Player, HumanObserver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trump_strategy = self.trump_strategy or SuitAmountTrumpStrategyBetterSkat()

    def next_card(self, hand: list[Card], valid_cards: list[Card]):
        print(f"{self.name}, your turn!")
        print(f"Your cards: {', '.join(f'{card} ({card_id})' for card_id, card in enumerate(hand))}")
        valid_cards = valid_cards
        while True:
            index = int(input("Which card would you like to play? "))
            if not 0 <= index < len(hand):
                print("Invalid Index!")
            else:
                card = hand[index]
                if card not in valid_cards:
                    print("You can't play that card.")
                else:
                    return card
