import os
import numpy as np
import sys

from pycard.model import deck
from pycard.agent import base, human


class Game:

    def __init__(self, debug: bool = False):
        """Class for managing both the game state (discard and stock) and players.

        Attributes:
            discard: list of deck.Cards, representing the discard pile
            stock: Deck of cards, representing remaining cards.
            players: dictionary mapping player names to player objects
        """
        self.discard = []
        self.stock = None
        self.players = {}
        self._debug = debug
        self._state_history = []

    @classmethod
    def initialize(cls, debug: bool = False, d: deck.Deck = None, num_players: int = 1, num_computers: int = 0):
        obj = cls()

        if not d:
            d = deck.Deck()
            d.shuffle()

        # Hand size of 7 for > 2 players, 13 for two players
        hand_size = 7
        if num_players + num_computers == 2:
            hand_size = 13

        hands, obj.stock = d.deal(hand_size, num_players + num_computers)
        obj.debug = debug

        for i in range(num_players + num_computers):
            name = f'p{i}' if i < num_players else f'c{i}'
            computer = False if i < num_players else True
            if computer:
                obj.players[name] = base.DummyAgent(name, hands[i], computer=computer)
            else:
                obj.players[name] = human.Human(name, hands[i], computer=computer)

        obj._build_state()
        return obj

    def play(self) -> None:
        """Main game loop. Allow players to draw/discard/meld until (1) they run out of cards or (2)
        the stock runs out of cards.
        """
        while True:
            for player_name, player in sorted(self.players.items()):
                self.play_turn(player)

                if (len(player.hand) == 0) or (len(self.stock) == 0):
                    scores = self.score_players()
                    print("============================================================")
                    print(f"Game over. {scores[0][0]} wins. Final scores:")
                    for player_name, score in scores:
                        print(f"\t{player_name}: {score}")
                    print("============================================================")
                    sys.exit(0)

            self._build_state()

    def play_turn(self, player: base.Agent):
        player.draw(self)
        player.meld(self)
        player.discard(self)

    def score_players(self):
        score_dict = {}
        for player_name, player in self.players.items():
            player_score = 0
            for meld in player.melds:
                player_score += sum(deck.CARD_VALUE_MAP[c[0]] for c in meld)

            player_score -= sum(deck.CARD_VALUE_MAP[c.rank] for c in player.hand)
            score_dict[player_name] = player_score

        return sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    def validate_meld(self, meld: ([deck.Card], str)) -> bool:
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
        rank_vals = sorted([deck.RANK_MAP[x.rank] for x in cards])
        if len(set(rank_vals)) == 1:
            return True

        # Check for run
        dists = [x - y for (x, y) in zip(rank_vals[1:], rank_vals)]
        suits = set([x.suit for x in cards])
        if len(suits) == 1 and all([x == 1 for x in dists]):
            return True

        return False

    def print_gamestate(self, current_player: str = None):
        # Print discard
        if not self._debug:
            os.system('clear')
            print(f"Current player: {current_player}")

        s = self._state_history[-1]
        for k, v in s.items():
            print(k, v)

        print(f"Stock remaining: {len(self.stock)}")

        if self._debug:
            print(f"Stock: {self.stock}")

        if not self.discard:
            print("Discard: empty")
        else:
            print(f"Discard: {deck.show_cards(self.discard)}")

        print()
        print("============================================================")

        # Print player melds
        table = []
        for _, player in sorted(self.players.items()):
            row = [player.name, '-'*len(player.name)]
            for i, meld in enumerate(player.melds):
                _, meldstr, ref = deck.show_meld(meld)
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
        if self._debug:
            for player_name, player in self.players.items():
                print(f"{player_name}'s hand: {deck.show_cards(player.hand)}")
        else:
            print(f"Your hand: {deck.show_cards(self.players[current_player].hand, sort=True)}")

        print()
        print("============================================================")
        # Print your options

    ################################################################################################
    # Private methods
    ################################################################################################
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
