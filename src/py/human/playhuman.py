import sys

import core.moves
import core.legalmoves
import human.display
import human.read

class Human:
    def __init__(self, white):
        self.white = white
        self.fout = sys.stdout
        self.fin = sys.stdin
        self.name = 'Human'

    def display_moves(self, gs, ms):
        numcols = 4
        colwidth = 14
        n = len(ms)
        numrows = ((n - 1) // numcols) + 1

        disp = [([''] * numcols) for i in range(numrows)]

        for i in range(n):
            s = str(i + 1)
            while len(s) < len(str(n)):
                s = ' ' + s

            s += ' '
            s += ms[i].name
            while len(s) < colwidth:
                s += ' '
            disp[i % numrows][i // numrows] = s

        for d in disp:
            self.fout.write(' '.join(d) + '\n')
        self.fout.write('\n')

    def read(self, n):
        return human.read.read_intrange('Enter move number:  ', n, self.fin, self.fout) - 1

    def choose_move(self, gs):
        extra_moves = [core.moves.Move.resign(), core.moves.Move.undo()]
        ms = core.legalmoves.moves.legalmoves(gs.state) + extra_moves
        self.fout.write('Turn ' + str((gs.turn + 1) // 2) + '\n')
        if len(gs.moves) > 0:
            self.fout.write('\nPrevious move: ' + gs.moves[-1].name + '\n')
        human.display.print_all(gs.state, out = self.fout, size = 3)
        self.display_moves(gs, ms)
        k = self.read(len(ms))
        return ms[k]

    def game_over(self, game):
        self.fout.write('Game over\n')
        if game.draw:
            self.fout.write('  Draw\n')
        else:
            if game.winner:
                self.fout.write('  White won\n')
            else:
                self.fout.write('  Black won\n')
