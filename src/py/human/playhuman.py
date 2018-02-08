import sys

import core.moves
import core.searchmoves as sm
import human.display

class Human:
    def __init__(self, white):
        self.white = white
        self.out = sys.stdout
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
            self.out.write(' '.join(d) + '\n')
        self.out.write('\n')

    def read(self, n):
        while True:
            self.out.write('Enter move number:  ')
            self.out.flush()
            choice = self.fin.readline().strip()
            self.out.write('\n')
            try:
                k = int(choice)
                if k > 0 and k <= n:
                    return k - 1
            except:
                pass

    def choose_move(self, gs):
        extra_moves = [core.moves.Move.resign(), core.moves.Move.undo()]
        ms = sm.searchmoves.legal_moves(gs.state) + extra_moves
        self.out.write('Turn ' + str((gs.turn + 1) // 2) + '\n')
        if len(gs.moves) > 0:
            self.out.write('\nPrevious move: ' + gs.moves[-1].name + '\n')
        human.display.print_all(gs.state, out = self.out, size = 3)
        self.display_moves(gs, ms)
        k = self.read(len(ms))
        return ms[k]

    def game_over(self, game):
        self.out.write('Game over\n')
        if game.draw:
            self.out.write('  Draw\n')
        else:
            if game.winner:
                self.out.write('  White won\n')
            else:
                self.out.write('  Black won\n')
