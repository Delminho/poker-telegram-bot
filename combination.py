from collections import Counter


class Combination:
    """Represent each player's combination"""
    def __init__(self, *card_lists):
        # Variables needed to recognize combination to update hand information
        self._all_cards = []
        for card_list in card_lists:
            self._all_cards.extend(card_list)
        self._all_cards_values = [card.value for card in self._all_cards]
        self._all_cards_suits = [card.suit for card in self._all_cards]
        self._all_cards_values_dict = Counter(self._all_cards_values)

        # Hand information needed to decide a winner
        self.rank = None     # Represents strength of hand, from 0 for High Card to 9 for Royal Flush
        self.rank_str = ''  # str representation of self.rank
        self.hand = []       # Stores 5 card list that form the best combination possible

        # Get hand information if cards amount is correct
        if len(self._all_cards) == 7:
            self._recognize_hand()


    def _recognize_hand(self):
        """Get all needed information about combination"""
        # Check if combination is Flush or Straight Flush or Royal Flush
        if self._is_flush():
            return

        # Check if combination is Four Of A Kind
        if self._is_four_of_a_kind():
            return

        # Check if combination is Full House
        if self._is_full_house():
            return

        # Check if combination is Straight
        if self._is_straight():
            return

        # Check if combination is Three Of A Kind
        if self._is_three_of_a_kind():
            return

        # Check if combination is Two Pair
        if self._is_two_pair():
            return

        # Check if combination is Pair
        if self._is_pair():
            return

        # No combination found so it's just High Card
        else:
            hand = sorted(self._all_cards, reverse=True)[:5]
            self._update_hand_information(0, hand)
            return

    def _update_hand_information(self, rank: int, hand: list):
        """For each recognized combination updates hand information"""
        rank_namings = ["High Card", "Pair", "Two Pair", "Three of a kind", "Straight", "Flush", "Full House",
                        "Four of a kind", "Straight Flush", "Royal Flush"]
        self.hand = hand
        self.rank = rank
        self.rank_str = rank_namings[rank]

    def _is_flush(self):
        """Checks is combination is flush, returns sorted list of all suited cards and updates hand information
         if it is and False if it isn't"""
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            if self._all_cards_suits.count(suit) >= 5:
                # Make list of all suited cards in descending order
                suited = [card for card in self._all_cards if card.suit == suit]
                suited.sort(reverse=True)

                # Check if it is Straight Flush
                suited_combination = Combination(suited)
                if suited_combination._is_straight():   # Check if combination of all suited cards is a straight
                    self._update_hand_information(8, list(suited_combination.hand))
                    # If highest card in Straight Flush is Ace then its Royal Flush
                    if suited_combination.hand[0].value == 14:
                        # In this case hand is already set so just need to change rank
                        self.rank = 9
                else:
                    # If hand is flush then it can't also be Quads or Full House so the best combination is found
                    self._update_hand_information(5, suited[:5])

                return True
        return False

    def _is_straight(self):
        """Checks is combination is straight, returns list of 5 highest straight cards if it is and False if it isn't"""
        leading_straight_values = []    # Needed to handle 6 or 7 values in a row situations
        for val in self._all_cards_values:
            if {val-1, val-2, val-3, val-4} <= set(self._all_cards_values):
                leading_straight_values.append(val)

        if {2, 3, 4, 5, 14} <= set(self._all_cards_values):  # Ace,2,3,4,5 straight situation
            leading_straight_values.append(5)

        try:
            leading_straight_value = max(leading_straight_values)     # No error means there is a straight
            # Making list of cards in straight
            hand = []
            values_in_straight = [leading_straight_value - i for i in range(5)]
            if 1 in values_in_straight: values_in_straight[-1] = 14   # To include ace in 5-high straight

            # For each value in straight find first card with that value and add it to combination
            for value in values_in_straight:
                for card in self._all_cards:
                    if card.value == value:
                        hand.append(card)
                        break

            self._update_hand_information(4, hand)
            return True

        except ValueError:  # No leading straight found, meaning no straight
            return False

    def _is_four_of_a_kind(self):
        """Check if combination is 4 of a kind, if so returns a 5card hand else returns False"""
        if 4 in self._all_cards_values_dict.values():
            # Finding value that repeats 4 times
            quads_value = self._all_cards_values_dict.most_common(1)[0][0]

            # Getting list of 4 cards with that value
            hand = [card for card in self._all_cards if card.value == quads_value]

            # Finding the highest 5th card and adding it to hand
            all_cards_sorted = sorted(self._all_cards, reverse=True)
            if all_cards_sorted[0].value != quads_value:
                tiebreaker = all_cards_sorted[0]
            else:
                tiebreaker = all_cards_sorted[1]
            hand.append(tiebreaker)

            # Update hand information
            self._update_hand_information(7, hand)
            return True
        else:
            return False

    def _is_full_house(self):
        """Check if combination is full house, if so returns a 5card hand else returns False"""
        # Three ways to get full house 3+2+1+1, 3+2+2, 3+3+1
        value_appearances = list(self._all_cards_values_dict.values())
        if value_appearances.count(3) == 2 or {3, 2} <= set(value_appearances): # Includes all 3 ways to get full house
            trips_values, duos_values, hand, trips_list, duos_list = [], [], [], [], []

            # Finding values of cards repeats three times(trips) and two times(duos)
            for card_value, appearances in self._all_cards_values_dict.items():
                if appearances == 3:
                    trips_values.append(card_value)
                if appearances == 2:
                    duos_values.append(card_value)

            # Handling 3+3+1 case
            if len(trips_values) > 1:
                trips_values.sort(reverse=True)
                duo = trips_values.pop()
                duos_values.append(duo)
            # Handling 3+2+2 case
            if len(duos_values) > 1:
                duos_values.sort(reverse=True)
                duos_values.pop()

            trips_values = trips_values[0]
            duos_values = duos_values[0]

            # Making a list of those cards that take part in Full House combination
            for card in self._all_cards:
                if card.value == trips_values:
                    trips_list.append(card)
                elif card.value == duos_values and len(duos_list) < 2:     # Second condition because of 3+3+1 situation
                    duos_list.append(card)
            hand = trips_list + duos_list

            self._update_hand_information(6, hand)
            return True
        else:
            return False

    def _is_three_of_a_kind(self):
        """Check if combination is Three Of A Kind, if so returns a 5card hand else returns False"""
        if 3 in self._all_cards_values_dict.values():
            # Find what value is repeated 3 times
            trips_value = self._all_cards_values_dict.most_common(1)[0][0]

            # Make a list of 3 trips cards and two top other cards
            hand = [card for card in self._all_cards if card.value == trips_value]     # 3 cards that form trips
            other_cards = [card for card in self._all_cards if not card.value == trips_value]
            tiebreaker = sorted(other_cards, reverse=True)[:2]     # 2 top cards out of left ones
            hand.extend(tiebreaker)

            self._update_hand_information(3, hand)
            return True
        else:
            return False

    def _is_two_pair(self):
        """Check if there is two pair if so returns 5card hand else returns False"""
        value_appearances = list(self._all_cards_values_dict.values())
        if value_appearances.count(2) > 1:
            # Find values that are repeated
            duo_values = [card_value for card_value, appearances in self._all_cards_values_dict.items() if appearances == 2]
            # If there is three pair it chooses two highest in descending order
            duo_values = sorted(duo_values, reverse=True)[:2]

            # Making lists of cards that form pairs and list of other cards
            duos_list_first = [card for card in self._all_cards if card.value == duo_values[0]]
            duos_list_second = [card for card in self._all_cards if card.value == duo_values[1]]
            other_cards = [card for card in self._all_cards if card.value not in duo_values]
            # Duos + Duos + the highest other card
            hand = duos_list_first + duos_list_second + sorted(other_cards, reverse=True)[:1]

            self._update_hand_information(2, hand)
            return True
        else:
            return False

    def _is_pair(self):
        """Check if there's a pair, if so returns a 5card hand with 2 first items paired"""
        if 2 in self._all_cards_values_dict.values():
            # Find value that repeats
            duo_value = self._all_cards_values_dict.most_common(1)[0][0]

            pair_list = [card for card in self._all_cards if card.value == duo_value]
            other_cards = [card for card in self._all_cards if card.value != duo_value]
            hand = pair_list + sorted(other_cards, reverse=True)[:3]

            self._update_hand_information(1, hand)
            return True

    def __gt__(self, other):
        return self.rank > other.rank or self.rank == other.rank and self.hand > other.hand

    def __lt__(self, other):
        return self.rank < other.rank or self.rank == other.rank and self.hand < other.hand

    def __eq__(self, other):
        return self.rank == other.rank and self.hand == other.hand
