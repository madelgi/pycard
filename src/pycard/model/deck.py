import enum
import random
from collections import namedtuple
from typing import List, Tuple


RANK_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}
CARD_VALUE_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 15
}
SUITS = ['H', 'S', 'C', 'D']

SYMBOLS = {
    'diamonds': '\u2666',
    'hearts': '\u2665',
    'clubs': '\u2663',
    'spades': '\u2660',
}

Card = namedtuple('Card', ['rank', 'suit'])


class Suit(enum.Enum):
    diamonds = 1
    hearts = 2
    clubs = 3
    spades = 4


class Deck:

    DECK_SIZE = 52

    def __init__(self, cards=None):
        """Initialize card deck.

        Arguments:
            cards:  List of cards to compose the deck. If blank, use the standard 52 card, four suit
                deck.
        """
        if not cards:
            self._cards = [Card(r, s) for r in RANK_MAP.keys() for s in Suit]
        else:
            self._cards = cards

    def shuffle(self) -> None:
        """Shuffle cards.
        """
        random.shuffle(self._cards)

    def draw(self) -> Card:
        """Draw a card from the deck.

        Returns:
            A single card.
        """
        try:
            return self._cards.pop()
        except IndexError:
            raise

    def deal(self, count: int, players: int) -> Tuple[List[List[Card]], 'Deck']:
        """Deal a set number of cards to a set number of players.

        Arguments:
            count: Number of cards to deal.
            players: Number of players to deal cards to.

        Returns:
            A tuple of (1) A list of card lists and (2) a new deck formed from the remaining cards.
        """
        if count * players > self.DECK_SIZE:
            raise ValueError("Deck not large enough.")

        hands = [self._cards[i * count: i * count + count] for i in range(players)]
        return (hands, Deck(cards=self._cards[count*players:]))

    def __len__(self):
        return len(self._cards)

    def __str__(self):
        return ' '.join([show_card(x) for x in self._cards])


def string_to_card(card_str: str) -> Card:
    if len(card_str) == 2:
        rank, suit = card_str[0], card_str[1]
    elif len(card_str) == 3:
        rank, suit = card_str[:2], card_str[2]
    else:
        raise ValueError(f"Invalid card string \"{card_str}\"")

    if (rank not in RANK_MAP.keys()) or (suit not in SUITS):
        raise ValueError("Invalid card string \"{card_str}\"")

    mapper = {'D': Suit.diamonds, 'C': Suit.clubs, 'H': Suit.hearts, 'S': Suit.spades}
    return Card(rank, mapper[suit])


def ascii_display_card(card: Card) -> str:
    suitmap = {'diamonds': 'D', 'spades': 'S', 'clubs': 'C', 'hearts': 'H'}
    return f'{card.rank}{suitmap[card.suit.name]}'


def show_card(card: Card) -> str:
    return u'{0}{1}'.format(card.rank, SYMBOLS[card.suit.name])


def show_cards(cards: [Card], sort: bool = False) -> str:
    if sort:
        cards = sorted(cards, key=lambda x: CARD_VALUE_MAP[x.rank])
    return ' '.join([show_card(x) for x in cards])


def show_meld(meld: [(Card, str)]) -> Tuple[str, List[str]]:
    cards, ref = meld
    if len(set(x.suit for x in cards)) == 1:
        meldtype = 'run'
    else:
        meldtype = 'set'

    return (meldtype, [show_card(x) for x in cards], ref)
