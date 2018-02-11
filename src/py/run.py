import random
import sys

import core.game
import players
import human.display
import human.read
import logger

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

    state = int(args[0])
    human.display.print_all(state, extra = True)

def replay(args):
    assert(len(args) == 1)

    log = logger.Logger.load(args[0])

    for move in log.moves:
        print('Turn {}: {}'.format(move['turn'], move['move']))
        human.display.print_all(move['state'], extra = True)
        human.read.wait()


commands = {
            'play' : play,
            'display' : display,
            'replay' : replay
        }

default_command = play

def run():
    if len(sys.argv) == 1:
        default_command([])
    elif len(sys.argv) > 1:
        command = commands[sys.argv[1].lower().strip()]
        command(sys.argv[2:])

if __name__ == "__main__":
    run()
