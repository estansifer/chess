import random
import sys

import core.game
import players

def play_game(white, black):
    g = core.game.Game()
    g.set_players(white(True), black(False))
    g.play()

def run():
    if len(sys.argv) == 1:
        p = [players.human, players.random]
        random.shuffle(p)
        play_game(p[0], p[1])
    if len(sys.argv) == 3:
        white = players.lookup_player_by_name(sys.argv[1])
        black = players.lookup_player_by_name(sys.argv[2])
        if white is None:
            print("Don't recognize player " + sys.argv[1])
        if black is None:
            print("Don't recognize player " + sys.argv[2])
        if not ((white is None) or (black is None)):
            play_game(white, black)

if __name__ == "__main__":
    run()
