"""
This is a program to play POKER online

Please follow the instructions!!
Author: Chenlin (Harry) Liu

Spades = 3
Hearts = 2
Diamonds = 1
Clubs = 0
Jack = 11
Queen = 12
King = 13

"""
import random


# First define Class for Cards

class Card:
    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank

    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    rank_names = [None, 'Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    def __str__(self):
        return '%s of %s' % (Card.rank_names[self.rank], Card.suit_names[self.suit])

    def __lt__(self, other):
        self.card = self.rank, self.suit
        other.card = other.rank, other.suit

        return self.card > other.card


# Test
# harry = Card(2, 11)
# kiwi = Card(1, 9)
# print(harry.__lt__(kiwi))


# Get the whole deck of cards
class Deck:

    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1, 14):
                card = Card(suit, rank)
                self.cards.append(card)
                random.shuffle(self.cards)  # Directly shuffle the cards after creation

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    # Test to print out the whole deck
    # deck = Deck()
    # print(deck)
    # Another way to shuffle the cards if not directly shuffling it after creation
    # Change the placement of the card (Swap)

    def shuffle(self):
        # for i in range(len(self.cards)-1, 0, -1):
        #     r = random.randint(0, i)
        #     self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

        random.shuffle(self.cards)

    # Test shuffling function
    # deck = Deck()
    # deck.shuffle()
    # print(deck)

    # Deal from the top of the deck:
    def pop_card(self):
        return self.cards.pop(0)

    def add_card(self, card):
        self.cards.append(card)

    def move_cards(self, hand, num):
        for i in range(num):
            hand.add_card(self.pop_card())

    def deal_hand(self, hand_num, card_num):
        handres = []
        for i in range(1, hand_num + 1):
            hand_i = Hand('Hand %d' % i)  # use i as an integer to label hand_i
            self.move_cards(hand_i, card_num)
            handres.append(hand_i)
        return handres


# Test if we could get two random cards
# deck = Deck()
# deck.shuffle()
# harry1 = deck.pop_card()
# harry2 = deck.pop_card()
#
# print(harry1, harry2)


# Create class hand
class Hand(Deck):

    def __init__(self, label=''):
        self.cards = []
        self.label = label

    # harry_hand = Hand('harry_hand')
    # deck = Deck()
    # harry_hand.move_cards(2)
    # print(harry_hand)

    # def deal_hands(self, hand_num, card_num):
    #     handres = []
    #     for i in range(hand_num):
    #         self.move_cards(card_num)
    #         handres.append(self)
    #     return handres


class Hist(dict):
    def __init__(self, seq=[]):
        for x in seq:
            self.count(x)

    def count(self, x, f=1):
        self[x] = self.get(x, 0) + f
        if self[x] == 0:
            del self[x]


####Get the number/ count of anything in the hands and delete it if it is 0###########
class Pokerhand(Hand):
    all_labels = ['straightflush', 'fourkind', 'fullhouse', 'flush', 'straight',
                  'threekind', 'twopair', 'pair', 'highcard']

    def make_histograms(self):
        self.suits = Hist()
        self.ranks = Hist()

        for i in self.cards:
            self.suits.count(i.suit)
            self.ranks.count(i.rank)

        self.sets = list(self.ranks.values())
        self.sets.sort(reverse=True)

    def has_highcard(self):
        return len(self.cards)

    def check_sets(self, *t):

        for need, have in zip(t, self.sets):
            if need > have:
                return False
        return True

    def has_pair(self):
        """Checks whether this hand has a pair."""
        return self.check_sets(2)

    def has_twopair(self):
        """Checks whether this hand has two pair."""
        return self.check_sets(2, 2)

    def has_threekind(self):
        """Checks whether this hand has three of a kind."""
        return self.check_sets(3)

    def has_fourkind(self):
        """Checks whether this hand has four of a kind."""
        return self.check_sets(4)

    def has_fullhouse(self):
        """Checks whether this hand has a full house."""
        return self.check_sets(3, 2)

    def has_flush(self):
        """Checks whether this hand has a flush."""
        for val in self.suits.values():
            if val >= 5:
                return True
        return False

    # def suit_cnt(self):
    #     self.suits = {}
    #
    #     for i in self.cards:
    #         self.suits[i.suit] = self.suits.get(i.suit, 0) + 1
    #
    # def is_flush(self):
    #     self.suit_cnt()
    #     for val in self.suits.values():
    #         if val >= 5:
    #             return True
    #     return False
    def has_straight(self):

        ranks = self.ranks.copy()
        ranks[14] = ranks.get(1, 0)  # Ace into 1?
        return self.in_a_row(ranks, 5)

    def in_a_row(self, ranks, n=5):
        count = 0
        for i in range(1, 15):
            if ranks.get(i, 0):
                count += 1
                if count == n:
                    return True
            else:
                count = 0
        return False

    def has_straightflush(self):
        d = {}
        for i in self.cards:
            d.setdefault(i.suit, Pokerhand()).add_card(i)

        for hand in d.values():
            if len(hand.cards) < 5:
                continue
            hand.make_histograms()
            if hand.has_straight():
                return True
        return False

    def classify(self):
        self.make_histograms()

        self.labels = []
        for label in Pokerhand.all_labels:
            f = getattr(self, 'has_' + label)
            if f():
                self.labels.append(label)


class PokerDeck(Deck):

    def deal_hands(self, hand_num=10, card_num=5):
        hands = []
        for i in range(hand_num):
            hand = Pokerhand()
            self.move_cards(hand, card_num)
            hand.classify()
            hands.append(hand)
        return hands


def main():
    lhist = Hist()
    n = 10000
    for i in range(n):
        if i % 1000 == 0:
            print(i)
        deck = PokerDeck()
        deck.shuffle()

        hands = deck.deal_hands(7, 7)
        for hand in hands:
            for label in hand.labels:
                lhist.count(label)

    total = 7.0 * n
    print(total, 'hands dealt: ')

    for label in Pokerhand.all_labels:
        freq = lhist.get(label, 0)
        if freq == 0:
            continue
        p = freq / total
        print('The chance for {} is {}'.format(label, p))


if __name__ == '__main__':
    main()
