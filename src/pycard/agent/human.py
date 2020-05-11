from typing import List

from pycard.model import deck
from pycard.agent.base import Agent
import pycard.model.game as game


class Human(Agent):

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

    def meld(self, game: 'game.Game') -> None:
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
                cards = [deck.string_to_card(c) for c in meld[1:]]
                meld = (cards, meld[0])
            else:
                cards = [deck.string_to_card(c) for c in meld]
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

    def discard(self, game: 'game.Game') -> None:
        game.print_gamestate(self.name)
        exit = False
        discard = input("Please select discard option: ")
        while not exit:
            try:
                card = deck.string_to_card(discard)
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
                print(f"Unable to find card \"{deck.ascii_display_card(card)}\" in your hand. Please try again.")
                discard = input("Please select discard option: ")
                continue
