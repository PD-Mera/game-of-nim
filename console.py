import argparse

from nim import SimpleNim, RegularNim, MisereNim, SplitNim
from players import Player

GAME_VARIANTS = {
    "simple": SimpleNim,
    "regular": RegularNim,
    "misere": MisereNim,
    "split": SplitNim,
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--game-variant", dest="game_variant", choices=GAME_VARIANTS.keys(), default="simple")
    parser.add_argument("--first", dest="first_player", choices=["Human", "AI"], default="AI")
    parser.add_argument("--second", dest="second_player", choices=["Human", "AI"], default="AI")
    args = parser.parse_args()

    nim_game = GAME_VARIANTS[args.game_variant]()
    player1 = Player(args.first_player, is_first_player=True)
    player2 = Player(args.second_player, is_first_player=False)

    return nim_game, player1, player2

if __name__ == "__main__":
    nim_game, player1, player2 = parse_args()
    nim_game.game_loop(player1=player1, player2=player2)
