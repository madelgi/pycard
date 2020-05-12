import abc
import random
from collections import defaultdict
from typing import List, Optional

from pycard.model import deck, game


class Agent(abc.ABC):

    def __init__(self, name: str, hand: [deck.Card], computer: bool = False):
        """Agent class.

        Arguments:
            name: Agent's name.
            hand: Agent's hand, a list of cards.
            computer: Whether the player is automated or not.

        """
        self.name: str = name
        self.computer: bool = computer
        self.hand: List = hand
        self.melds: List = []

    @abc.abstractmethod
    def draw(self, game: 'game.Game'):
        pass

    @abc.abstractmethod
    def meld(self, game: 'game.Game'):
        pass

    @abc.abstractmethod
    def discard(self, game: 'game.Game'):
        pass


class DummyAgent(Agent):
    def __init__(self, name: str, hand: [deck.Card], computer: bool = False):
        """This is the simplest agent I could come up with. Its behavior at each stage
        is defined as follows:

            1. draw: Always take 1 card from stock (never discard)
            2. meld: Use find_meld to determine if hand contains a meld, and if so, play it. Do
                 not meld off of other players hands.
            3. discard: Just pop the top-value off the player's hand.
        """
        self.name: str = name
        self.computer: bool = computer
        self.hand: List = hand
        self.melds: List = []

    def draw(self, game: 'game.Game') -> None:
        c = [game.stock.draw()]
        self.hand.extend(c)

    def meld(self, game: 'game.Game') -> None:
        melds = self._find_meld(game)
        if melds:
            # Choose the top scoring meld
            meld = sorted(
                [(meld, sum([deck.CARD_VALUE_MAP[x.rank] for x in meld])) for meld in melds],
                key=lambda x: x[1],
                reverse=True)[0][0]
            for card in meld:
                self.hand.remove(card)

            self.melds.append(meld)

    def discard(self, game: 'game.Game') -> None:
        meld_cards = set([x for m in self._find_meld(game) for x in m])
        game.discard.append(self.hand.pop())

    def _find_meld(self, game: 'game.Game') -> List[List[deck.Card]]:
        def get_ascending(cards: List[deck.Card]) -> Optional[List[deck.Card]]:
            runs, start_run, end_run = [], 0, 0
            for i, (c1, c2) in enumerate(zip(cards, cards[1:])):
                if end_run - start_run > 2:
                    runs.append(cards[start_run:end_run])

                if deck.CARD_VALUE_MAP[c2.rank] - deck.CARD_VALUE_MAP[c1.rank] == 1:
                    end_run += 1
                else:
                    start_run, end_run = i + 1, i + 1

            return runs

        melds = []

        # Determine sets
        sets = defaultdict(list)
        for card in self.hand:
            sets[card.rank].append(card)

        for s in sets.values():
            if len(s) >= 3:
                melds.append(s)

        # Determine runs
        suitdict = defaultdict(list)
        for card in self.hand:
            suitdict[card.suit].append(card)

        suitdict = {k: sorted(v, key=lambda x: deck.CARD_VALUE_MAP[x.rank]) for k, v in suitdict.items()}

        for cs in suitdict.values():
            runs = get_ascending(cs)
            if runs:
                melds.extend(runs)

        return sorted(melds, key=lambda x: len(x), reverse=True)
