import argparse

from pycard.model import game


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--computers', type=int, default=0, help='Number of computer players')
    parser.add_argument('-n', '--num_players', type=int, default=1, help='Number of human players')
    parser.add_argument('-d', '--debug', action='store_true', help='Print debug information')

    args = parser.parse_args()

    g = game.Game(debug=args.debug).initialize(num_players=args.num_players, num_computers=args.computers)
    g.play()
