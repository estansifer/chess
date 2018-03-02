import random
import sys
import gmpy2

import core.game
import players
import human.display
import human.read
import logger

usage_str = """
python run.py usage
    Display this message.

python run.py play
    Play a game of chess.

python run.py display <state>
    Given an integer representing a chess-board state, display it.

python run.py replay <filename>
    Replay a chess game that was logged in the specified file.
"""

def usage(args):
    print(usage_str)

def play(args):
    def print_player_list():
        print('')
        print('    Player choices:')
        for i, player in enumerate(players.players):
            print((' ' * 8) + '[' + str(i + 1) + ']  ' + player.name)

    randomize = human.read.read_boolean('Randomize sides [Y/n]?  ', True)

    if randomize:
        titles = ['Player 1', 'Player 2']
    else:
        titles = ['White player', 'Black player']

    p = []
    for title in titles:
        print_player_list()
        j = human.read.read_intrange(title + ':  ', len(players.players)) - 1
        p.append(players.players[j])

    if randomize:
        random.shuffle(p)

    g = core.game.Game()
    g.set_players(p[0].factory(True), p[1].factory(False))
    g.play()

def display(args):
    assert(len(args) == 1)

    state = gmpy2.mpz(int(args[0]))
    human.display.print_all(state, extra = True)

def replay(args):
    assert(len(args) == 1)

    log = logger.Logger.load(args[0])

    print('White:', log.players['white'])
    print('Black:', log.players['black'])

    for move in log.moves:
        print('Turn {}: {}'.format(move['turn'], move['move']))
        human.display.print_all(move['state'], extra = True)
        human.read.wait()


commands = {
            'play' : play,
            'display' : display,
            'replay' : replay,
            'usage' : usage
        }

default_command = usage

def run():
    if len(sys.argv) == 1:
        default_command([])
    elif len(sys.argv) > 1:
        command_name = sys.argv[1].lower().strip()
        command = commands.get(command_name, default_command)
        command(sys.argv[2:])

if __name__ == "__main__":
    run()
