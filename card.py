import csv

class Card:
    """Represents card for poker"""
    def __init__(self, value: int, suit: str):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"Card({self.value}, '{self.suit}')"

    def __str__(self):
        if self.suit == 'hearts':
            suit_str = "♥️"
        elif self.suit == 'diamonds':
            suit_str = "♦️"
        elif self.suit == 'clubs':
            suit_str = "♣️"
        elif self.suit == 'spades':
            suit_str = "♠️"

        if self.value <= 10:
            value_str = self.value
        elif self.value == 11:
            value_str = "Jack"
        elif self.value == 12:
            value_str = "Queen"
        elif self.value == 13:
            value_str = "King"
        elif self.value == 14:
            value_str = "Ace"

        return f"|{suit_str} {value_str} {suit_str}|"

    # Comparing cards by their values
    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value
