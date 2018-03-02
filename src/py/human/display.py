import sys

import core.position as pos
import core.legalmoves

def display_piece(color_piece):
    if color_piece == 0:
        return '.'
    piece = color_piece & pos.mask_piece
    if (color_piece & pos.mask_white_piece) > 0:
        return '?KQRBNP?'[piece]
    if (color_piece & pos.mask_black_piece) > 0:
        return '?kqrbnp?'[piece]
    return '?'

def display_board(state, white = '.', black = ' ', size = 2):
    checkers = [[None for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            checkers[i][j] = (white + black)[(i + j) % 2]

    pieces = [[None for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            c = display_piece(
                    (state >> pos.Square(8 * (7 - i) + j).bits)
                    & pos.mask_square)
            if c == '.':
                pieces[i][j] = checkers[i][j]
            else:
                pieces[i][j] = c

    if size == 1:
        return [''.join(row) for row in pieces]
    elif size == 2:
        board = [[[' '] * 4 for j in range(8)] for i in range(8 * 2)]
        for i in range(8):
            for j in range(8):
                board[2 * i][j][0] = pieces[i][j]
                board[2 * i][j][2] = checkers[i][j]
                board[2 * i + 1][j][0] = checkers[i][j]
                board[2 * i + 1][j][2] = checkers[i][j]
        return [''.join([''.join(sq) for sq in row]) for row in board]
    elif size == 3:
        board = [[[' '] * 6 for j in range(8)] for i in range(8 * 3)]
        for i in range(8):
            for j in range(8):
                board[3 * i][j][0] = checkers[i][j]
                board[3 * i][j][2] = checkers[i][j]
                board[3 * i][j][4] = checkers[i][j]
                board[3 * i + 1][j][0] = checkers[i][j]
                board[3 * i + 1][j][2] = pieces[i][j]
                board[3 * i + 1][j][4] = checkers[i][j]
                board[3 * i + 2][j][0] = checkers[i][j]
                board[3 * i + 2][j][2] = checkers[i][j]
                board[3 * i + 2][j][4] = checkers[i][j]
        return [''.join([''.join(sq) for sq in row]) for row in board]
    # elif size == 3:
        # board = [[[' '] * 6 for j in range(8)] for i in range(8 * 3)]
        # for i in range(8):
            # for j in range(8):
                # board[3 * i][j][0] = pieces[i][j]
                # board[3 * i][j][3] = checkers[i][j]
                # board[3 * i + 1][j][0] = checkers[i][j]
                # board[3 * i + 1][j][3] = checkers[i][j]
        # return [''.join([''.join(sq) for sq in row]) for row in board]

def display_extra_bits(state, extra = False):
    castling = ''
    if (state & (1 << pos.bits_castle_K)) > 0:
        castling += 'K'
    if (state & (1 << pos.bits_castle_Q)) > 0:
        castling += 'Q'
    if (state & (1 << pos.bits_castle_k)) > 0:
        castling += 'k'
    if (state & (1 << pos.bits_castle_q)) > 0:
        castling += 'q'

    start = (state >> pos.bits_square_from) & 63
    end = (state >> pos.bits_square_to) & 63
    status = 'Last move {} to {}. '.format(
            pos.Square(start).symbol,
            pos.Square(end).symbol)

    more = ''
    if extra:
        more = '\nKings: '
        more += pos.Square((state >> pos.bits_king_white) & 63).symbol
        more += ', '
        more += pos.Square((state >> pos.bits_king_black) & 63).symbol

    if castling == '':
        return status + 'No castling rights.' + more
    else:
        return status + 'Can castle: ' + castling + more

def print_board(state, white = '.', black = ' ', size = 3, out = sys.stdout):
    board = display_board(state, white, black, size)
    for row in board:
        out.write((' ' * 8) + row + '\n')
    out.write('\n')
    out.flush()

def print_all(state, white = '.', black = ' ', size = 3, out = sys.stdout, extra = False):
    print_board(state, white, black, size)
    out.write(display_extra_bits(state, extra) + '\n\n')
    print('In check:', core.legalmoves.moves.in_check(state))
    print('White\'s turn?', core.position.white_turn(state))
    out.flush()

if __name__ == "__main__":
    state = int(sys.argv[1])
    print_all(state, extra = True)
