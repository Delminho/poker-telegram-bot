import csv
import random

from card import Card


class Deck:
    """Represent poker deck of cards"""
    def __init__(self):
        """Returns full deck of cards from a full_deck.csv file as a list"""
        deck = []

        with open('full_deck.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header

            # Reading from file each card and creating Card objects
            for row in reader:
                value, suit = row
                card = Card(int(value), suit)
                deck.append(card)

            self.deck = deck

    def take_card(self):
        """Returns random card and removes it from a deck"""
        random_card = random.choice(self.deck)
        # Can't use remove() because cards are compared only by values(to recognize combinations easier)
        self.deck = [card for card in self.deck if card.value != random_card.value or card.suit != random_card.suit]
        return random_card
