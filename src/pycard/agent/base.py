import abc
from collections import defaultdict
from typing import List

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
    def draw(self):
        pass

    @abc.abstractmethod
    def meld(self):
        pass

    @abc.abstractmethod
    def discard(self):
        pass


class DummyAgent(Agent):
    def __init__(self, name: str, hand: [deck.Card], computer: bool = False):
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

    def draw(self, game: 'game.Game') -> None:
        """TODO placeholder, just pop off of stock.
        """
        c = [game.stock.draw()]
        self.hand.extend(c)

    def meld(self, game: 'game.Game') -> None:
        melds = self.find_meld()
        if melds:
            meld = melds[0]
            for card in meld:
                self.hand.remove(card)

            self.melds.append(meld)

    def discard(self, game: 'game.Game') -> None:
        """TODO placeholder, discard top.
        """
        game.discard.append(self.hand.pop())

    def find_meld(self) -> List[List[deck.Card]]:
        melds = []

        # Determine sets
        sets = defaultdict(list)
        for card in self.hand:
            sets[card.rank].append(card)

        for s in sets.values():
            if len(s) >= 3:
                melds.append(s)

        return sorted(melds, key=lambda x: len(x), reverse=True)
