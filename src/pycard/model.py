from collections import namedtuple, defaultdict
import copy
import enum
import json
import os
import pandas as pd
import numpy as np
import random
import sys
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


def null_state():
    gs = pd.DataFrame(np.zeros((4, 13), dtype=int))
    gs.columns = RANK_MAP.keys()
    gs.index = SUITS
    return gs


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


class Player:

    def __init__(self, name: str, hand: [Card], computer: bool = False):
        """Player class.

        Arguments:
            name: Player's name.
            hand: Player's hand, a list of cards.
            computer: Whether the player is automated or not.

        """
        self.name: str = name
        self.computer: bool = computer
        self.hand: List = hand
        self.melds: List = []

    def draw(self, game: 'Game') -> None:
        """Draw a card from stock or discard and add it to hand.

        Arguments:
            game: A game instance.
        """
        if self.computer:
            self._draw_auto(game)
        else:
            self._draw_interactive(game)

    def discard(self, game: 'Game') -> None:
        """Discard a card from hand to game discard.

        Arguments:
            game: A game instance.
        """
        if self.computer:
            self._discard_auto(game)
        else:
            self._discard_interactive(game)

    def meld(self, game: 'Game') -> None:
        """Form melds using own hand and game melds.

        Arguments:
            game: A game instance.
        """
        if self.computer:
            self._meld_auto(game)
        else:
            self._meld_interactive(game)

    def _draw_auto(self, game: 'Game') -> None:
        """TODO placeholder, just pop off of stock.
        """
        c = [game.stock.draw()]
        self.hand.extend(c)

    def _draw_interactive(self, game: 'Game') -> None:
        game.print_gamestate(self.name)
        exit = False
        draw = input("Please select draw option: ").lower().strip()
        while not exit:
            if len(draw) == 0:
                game.print_gamestate(self.name)
                print("Please enter a non-empty draw option")
                draw = input("Please select draw option (<S>/<D#>): ").lower().strip()
                continue

            if draw == 's':
                c = [game.stock.draw()]
                exit = True
            elif draw[0] == 'd':
                try:
                    num_discard = int(draw[1])
                except Exception:
                    game.print_gamestate(self.name)
                    print("Must specify number of cards to draw from discard, e.g., \"D3\" draw 3 from discard.")
                    draw = input("Please select draw option (<S>/<D#>): ").lower().strip()
                    continue

                if num_discard > len(game.discard):
                    game.print_gamestate(self.name)
                    print("Cannot draw more than number currently in discard.")
                    draw = input("Please select draw option (<S>/<D#>): ").lower().strip()
                    continue

                c = []
                for _ in range(num_discard):
                    c.append(game.discard.pop())
                exit = True
            else:
                pass

        self.hand.extend(c)

    def _meld_auto(self, game: 'Game') -> None:
        melds = find_meld(self.hand)
        if melds:
            meld = melds[0]
            for card in meld:
                self.hand.remove(card)

            self.melds.append(meld)

    def _meld_interactive(self, game: 'Game') -> None:
        game.print_gamestate(self.name)
        meld = input("Specify meld or type 'discard' to discard and end your turn: ")
        while True:
            meld = meld.strip()

            if meld.lower() == 'discard':
                break

            meld = meld.split()
            if len(meld) < 0:
                pass

            if ':' in meld[0]:
                # Build off of other players
                cards = [string_to_card(c) for c in meld[1:]]
                meld = (cards, meld[0])
            else:
                cards = [string_to_card(c) for c in meld]
                meld = (cards, None)

            if game.validate_meld(meld):
                for card in cards:
                    self.hand.remove(card)

                self.melds.append(meld)
                meld = input("Specify meld or type 'discard' to discard and end your turn: ")
            else:
                game.print_gamestate(self.name)
                meld = input("Invalid meld. Specify meld or type 'discard' to discard and end your turn: ")
                continue

    def _discard_auto(self, game: 'Game') -> None:
        """TODO placeholder, discard top.
        """
        game.discard.append(self.hand.pop())

    def _discard_interactive(self, game: 'Game') -> None:
        game.print_gamestate(self.name)
        exit = False
        discard = input("Please select discard option: ")
        while not exit:
            try:
                card = string_to_card(discard)
            except ValueError or IndexError:
                game.print_gamestate(self.name)
                print("Please enter a discard choice of the form \"<RANK><SUIT>\" (e.g., \"4C\" for four of clubs)")
                discard = input("Please select discard option: ")
                continue

            for i, c in enumerate(self.hand):
                if c == card:
                    self.hand.pop(i)
                    game.discard.append(c)
                    exit = True
                    break
            else:
                game.print_gamestate(self.name)
                print(f"Unable to find card \"{ascii_display_card(card)}\" in your hand. Please try again.")
                discard = input("Please select discard option: ")
                continue


class Game:

    def __init__(self):
        """Class for managing both the game state (discard and stock) and players.

        Attributes:
            discard: list of Cards, representing the discard pile
            stock: Deck of cards, representing remaining cards.
            players: dictionary mapping player names to player objects
        """
        self.discard = []
        self.stock = None
        self.players = {}
        self._state_history = []

    def _build_state(self):
        state_dict = {}
        state_dict['stock'] = list(self.stock._cards)
        state_dict['discard'] = list(self.discard)
        state_dict['players'] = {}

        for player_name, player in self.players.items():
            state_dict['players'][player_name] = {}
            state_dict['players'][player_name]['hand'] = list(player.hand)
            state_dict['players'][player_name]['melds'] = list(player.melds)

        self._state_history.append(state_dict)

    def initialize(self, d: Deck = None, num_players: int = 1, num_computers: int = 0):
        if not d:
            d = Deck()
            d.shuffle()

        hands, self.stock = d.deal(7, num_players + num_computers)

        for i in range(num_players + num_computers):
            name = f'p{i}' if i < num_players else f'c{i}'
            computer = False if i < num_players else True
            self.players[name] = Player(name, hands[i], computer=computer)

        self._build_state()

    def play(self) -> None:
        """Main game loop. Allow players to draw/discard/meld until (1) they run out of cards or (2)
        the stock runs out of cards.
        """
        while True:
            for player_name, player in sorted(self.players.items()):
                self.play_turn(player)

                if (len(player.hand) == 0) or (len(self.stock) == 0):
                    score_dict = self.score_players()
                    print("============================================================")
                    print("Game over. Final scores:")
                    for player_name, score in score_dict:
                        print(f"\t{player_name}: {score}")
                    print("============================================================")
                    sys.exit(0)

            self._build_state()

    def play_turn(self, player: Player):
        player.draw(self)
        player.meld(self)
        player.discard(self)

    def score_players(self):
        score_dict = {}
        for player_name, player in self.players.items():
            player_score = 0
            for meld in player.melds:
                player_score += sum(CARD_VALUE_MAP[c[0]] for c in meld)

            player_score -= sum(CARD_VALUE_MAP[c] for c in player.hand)
            score_dict[player_name] = player_score

        return score_dict

    def validate_meld(self, meld: ([Card], str)) -> bool:
        """Validate a meld given other players melds.
        """
        cards, ref = meld
        if ref:
            player, index = ref.split(':')
            addtl_cards, _ = self.players[player].melds[index]
            cards.extend(addtl_cards)

        if len(cards) < 3:
            return False

        # Check for set
        rank_vals = sorted([RANK_MAP[x.rank] for x in cards])
        if len(set(rank_vals)) == 1:
            return True

        # Check for run
        dists = [x - y for (x, y) in zip(rank_vals[1:], rank_vals)]
        if all([x == 1 for x in dists]):
            return True

        return False

    def print_gamestate(self, current_player: str = None, debug: bool = False):
        # Print discard
        if not debug:
            os.system('clear')
            print(f"Current player: {current_player}")

        s = self._state_history[-1]
        for k, v in s.items():
            print(k, v)

        print(f"Stock remaining: {len(self.stock)}")

        if debug:
            print(f"Stock: {self.stock}")

        if not self.discard:
            print("Discard: empty")
        else:
            print(f"Discard: {show_cards(self.discard)}")

        print()
        print("============================================================")

        # Print player melds
        table = []
        for _, player in sorted(self.players.items()):
            row = [player.name, '-'*len(player.name)]
            for i, meld in enumerate(player.melds):
                _, meldstr, ref = show_meld(meld)
                if ref:
                    row.append(u"{0}: {1} (ref: {2})".format(i, ' '.join(meldstr), ref))
                else:
                    row.append(u"{0}: {1}".format(i, ' '.join(meldstr)))

            table.append(row)

        maxlen = max([len(x) for x in table])
        for row in table:
            if len(row) < maxlen:
                row += [''] * (maxlen - len(row))

        table = np.array(table).T
        fmt_string = u" ".join(["{:<20}"] * len(self.players))
        for row in table:
            print(fmt_string.format(*list(row)))

        print()
        print("============================================================")

        # Print current players hand
        if debug:
            for player_name, player in self.players.items():
                print(f"{player_name}'s hand: {show_cards(player.hand)}")
        else:
            print(f"Your hand: {show_cards(self.players[current_player].hand, sort=True)}")

        print()
        print("============================================================")
        # Print your options


####################################################################################################
# Utility functions
####################################################################################################
def find_meld(cards: List[Card]) -> List[List[Card]]:
    melds = []

    # Determine sets
    sets = defaultdict(list)
    for card in cards:
        sets[card.rank].append(card)

    for s in sets.values():
        if len(s) >= 3:
            melds.append(s)

    return sorted(melds, key=lambda x: len(x), reverse=True)


def show_card(card: Card) -> str:
    return u'{0}{1}'.format(card.rank, SYMBOLS[card.suit.name])


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


def validate_meld(meld: ([Card], str), players: dict):
    breakpoint()
    cards, ref = meld
    if ref:
        player, index = ref.split(':')
        addtl_cards, _ = players[player].melds[index]
        cards.extend(addtl_cards)

    if len(meld) < 3:
        return False

    # Check for set
    rank_vals = sorted([RANK_MAP[x.rank] for x in meld])
    if len(set(rank_vals)) == 1:
        return True

    # Check for run
    dists = [x - y for (x, y) in zip(rank_vals[1:], rank_vals)]
    if all([x == 1 for x in dists]):
        return True

    return False


def show_cards(cards: [Card], sort: bool = False) -> str:
    if sort:
        cards = sorted(cards, key=lambda x: CARD_VALUE_MAP[x.rank])
    return ' '.join([show_card(x) for x in cards])


def ascii_display_card(card: Card) -> str:
    suitmap = {'diamonds': 'D', 'spades': 'S', 'clubs': 'C', 'hearts': 'H'}
    return f'{card.rank}{suitmap[card.suit.name]}'


def show_meld(meld: [(Card, str)]) -> Tuple[str, List[str]]:
    cards, ref = meld
    if len(set(x.suit for x in cards)) == 1:
        meldtype = 'run'
    else:
        meldtype = 'set'

    return (meldtype, [show_card(x) for x in cards], ref)


if __name__ == '__main__':
    g = Game()
    g.initialize()
    g.play()
    # print(null_state())
