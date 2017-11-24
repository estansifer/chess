import sys
import position
import searchmoves

def piece_symbol(color_piece):
    if color_piece == 0:
        return '.'
    piece = color_piece & position.bits_piece_mask
    if (color_piece & position.bits_white_piece) > 0:
        return '?KQRBNP?'[piece]
    if (color_piece & position.bits_black_piece) > 0:
        return '?kqrbnp?'[piece]
    return '?'

class Human:
    def __init__(self, white):
        self.white = white
        self.out = sys.stdout
        self.fin = sys.stdin
        self.name = 'Human'

    def display_board(self, gs):
        def p(s):
            self.out.write(s + '\n')

        def sq(row, col):
            return piece_symbol(
                (gs.state >> position.Square(8 * row + col).bits)
                    & position.bits_square_mask)

        board = [[' ' for i in range(8 * 2)] for j in range(8 * 2)]

        for i in range(8):
            for j in range(8):
                c = '. '[(i + j) % 2]
                board[i * 2][j * 2] = c
                board[i * 2 + 1][j * 2] = c
                board[i * 2][j * 2 + 1] = c
                board[i * 2 + 1][j * 2 + 1] = c
                c = sq(7 - i, j)
                if c != '.':
                    board[i * 2][j * 2] = c

        if not (gs.last_move is None):
            p('')
            p('Previous move: ' + gs.last_move.name)

        p('')
        for i in range(8):
            p((' ' * 8) + '  '.join(board[2 * i]))
            p((' ' * 8) + '  '.join(board[2 * i + 1]))
            p('')

    def display_moves(self, gs, names):
        numcols = 4
        colwidth = 14
        n = len(names)
        numrows = ((n - 1) // numcols) + 1

        disp = [([''] * numcols) for i in range(numrows)]

        for i in range(n):
            s = str(i + 1)
            while len(s) < len(str(n)):
                s = ' ' + s

            s += ' '
            s += names[i]
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
        ms = searchmoves.legal_moves(gs.state)
        self.out.write('Turn ' + str((gs.turn + 1) // 2) + '\n')
        self.display_board(gs)
        self.display_moves(gs, [m.name for m in ms] + ['Resign'])
        ms.append(None)
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

    def show_legality(self, gs, move):
        print(self.white)
        gs = gs.copy()
        gs.state = (gs.state & move.check_mask) ^ move.check_result
        self.display_board(gs)
        self.out.write(str(gs.state >> position.bits_board_size) + '\n')
        self.out.write(move.name + '\n')
        self.out.flush()
