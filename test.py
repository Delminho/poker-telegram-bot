import unittest

from combination import Combination
from card import Card


class CombinationTest(unittest.TestCase):
    def setUp(self):
        self.royal_flush = Combination([
            Card(10, 'hearts'), Card(11, 'hearts'), Card(13, 'hearts'), Card(10, 'spades'), Card(12, 'hearts'),
            Card(14, 'hearts'), Card(8, 'diamonds')
        ])
        self.royal_flush_combination = [
            Card(14, 'hearts'), Card(13, 'hearts'), Card(12, 'hearts'), Card(11, 'hearts'), Card(10, 'hearts')
        ]

        self.straight_flush = Combination([
            Card(10, 'hearts'), Card(11, 'hearts'), Card(13, 'hearts'), Card(7, 'spades'), Card(12, 'hearts'),
            Card(9, 'hearts'), Card(8, 'diamonds')
        ])
        self.straight_flush_combination = [
            Card(13, 'hearts'), Card(12, 'hearts'), Card(11, 'hearts'), Card(10, 'hearts'), Card(9, 'hearts')
        ]

        self.quads = Combination([
            Card(8, 'hearts'), Card(9, 'hearts'), Card(10, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(8, 'spades'), Card(12, 'spades')
        ])
        self.quads_combination = [
            Card(8, 'hearts'), Card(8, 'diamonds'), Card(8, 'clubs'), Card(8, 'spades'), Card(12, 'spades')
        ]

        # 3 + 2 + 1 + 1
        self.full1 = Combination([
            Card(9, 'spades'), Card(9, 'hearts'), Card(10, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(8, 'spades'), Card(12, 'spades')
        ])
        self.full1_combination = [
            Card(8, 'diamonds'), Card(8, 'clubs'), Card(8, 'spades'), Card(9, 'spades'), Card(9, 'hearts')
        ]
        # 3 + 3 + 1
        self.full2 = Combination([
            Card(9, 'spades'), Card(9, 'hearts'), Card(9, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(8, 'spades'), Card(12, 'spades')
        ])
        self.full2_combination = [
            Card(9, 'spades'), Card(9, 'hearts'), Card(9, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs')
        ]
        # 3 + 2 + 2
        self.full3 = Combination([
            Card(2, 'hearts'), Card(3, 'hearts'), Card(4, 'hearts'), Card(2, 'diamonds'), Card(3, 'diamonds'),
            Card(4, 'diamonds'), Card(2, 'clubs')
        ])
        self.full3_combination = [
            Card(2, 'hearts'), Card(2, 'diamonds'), Card(2, 'clubs'), Card(4, 'diamonds'), Card(4, 'hearts')
        ]

        self.flush = Combination([
            Card(2, 'hearts'), Card(4, 'hearts'), Card(5, 'hearts'), Card(6, 'hearts'), Card(8, 'spades'),
            Card(9, 'hearts'), Card(11, 'hearts')
        ])
        self.flush_combination = [
            Card(11, 'hearts'), Card(9, 'hearts'), Card(6, 'hearts'), Card(5, 'hearts'), Card(4, 'hearts')
        ]

        self.straight = Combination([
            Card(2, 'hearts'), Card(3, 'diamonds'), Card(4, 'hearts'), Card(5, 'hearts'), Card(8, 'spades'),
            Card(14, 'clubs'), Card(10, 'clubs')
        ])
        self.straight_combination = [
            Card(5, 'hearts'), Card(4, 'hearts'), Card(3, 'diamonds'), Card(2, 'hearts'), Card(14, 'clubs')
        ]

        self.trips = Combination([
            Card(7, 'hearts'), Card(9, 'hearts'), Card(10, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(8, 'spades'), Card(12, 'spades')
        ])
        self.trips_combination = [
            Card(8, 'diamonds'), Card(8, 'clubs'), Card(8, 'spades'), Card(12, 'spades'), Card(10, 'diamonds')
        ]

        self.two_pair = Combination([
            Card(9, 'spades'), Card(9, 'hearts'), Card(10, 'diamonds'),Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(5, 'spades'), Card(12, 'spades')
        ])
        self.two_pair_combination = [
            Card(9, 'spades'), Card(9, 'hearts'), Card(8, 'diamonds'), Card(8, 'clubs'), Card(12, 'spades')
        ]

        self.pair = Combination([
            Card(7, 'hearts'), Card(9, 'hearts'), Card(10, 'diamonds'), Card(8, 'diamonds'), Card(8, 'clubs'),
            Card(13, 'spades'), Card(12, 'spades')
        ])
        self.pair_combination = [
            Card(8, 'diamonds'), Card(8, 'clubs'), Card(13, 'spades'), Card(12, 'spades'), Card(10, 'diamonds')
        ]

        self.high = Combination([
            Card(7, 'hearts'), Card(9, 'hearts'), Card(10, 'diamonds'), Card(8, 'diamonds'), Card(3, 'clubs'),
            Card(13, 'spades'), Card(12, 'spades')
        ])
        self.high_combination = [
            Card(13, 'spades'), Card(12, 'spades'), Card(10, 'diamonds'), Card(9, 'hearts'), Card(8, 'diamonds')
        ]

    def test_royal_flush(self):
        self.assertEqual(self.royal_flush.rank, 9)
        self.assertEqual(self.royal_flush.hand, self.royal_flush_combination)

    def test_straight_flush(self):
        self.assertEqual(self.straight_flush.rank, 8)
        self.assertEqual(self.straight_flush.hand, self.straight_flush_combination)

    def test_quads(self):
        self.assertEqual(self.quads.rank, 7)
        self.assertEqual(self.quads.hand, self.quads_combination)

    def test_full_house(self):
        self.assertEqual(self.full1.rank, 6)
        self.assertEqual(self.full1.hand, self.full1_combination)
        self.assertEqual(self.full2.rank, 6)
        self.assertEqual(self.full2.hand, self.full2_combination)
        self.assertEqual(self.full3.rank, 6)
        self.assertEqual(self.full3.hand, self.full3_combination)

    def test_flush(self):
        self.assertEqual(self.flush.rank, 5)
        self.assertEqual(self.flush.hand, self.flush_combination)

    def test_straight(self):
        self.assertEqual(self.straight.rank, 4)
        self.assertEqual(self.straight.hand, self.straight_combination)

    def test_trips(self):
        self.assertEqual(self.trips.rank, 3)
        self.assertEqual(self.trips.hand, self.trips_combination)

    def test_two_pair(self):
        self.assertEqual(self.two_pair.rank, 2)
        self.assertEqual(self.two_pair.hand, self.two_pair_combination)

    def test_pair(self):
        self.assertEqual(self.pair.rank, 1)
        self.assertEqual(self.pair.hand, self.pair_combination)

    def test_high_card(self):
        self.assertEqual(self.high.rank, 0)
        self.assertEqual(self.high.hand, self.high_combination)

    def test_combinations_comparison(self):
        # TODO More tests
        self.assertTrue(self.trips > self.high)
        self.assertTrue(self.full2 > self.full1 > self.full3)


if __name__ == '__main__':
    unittest.main()
