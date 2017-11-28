import sys
import position
import searchmoves

def display_piece(color_piece):
    if color_piece == 0:
        return '.'
    piece = color_piece & position.mask_piece
    if (color_piece & position.mask_white_piece) > 0:
        return '?KQRBNP?'[piece]
    if (color_piece & position.mask_black_piece) > 0:
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
                    (state >> position.Square(8 * (7 - i) + j).bits)
                    & position.mask_square)
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

def display_extra_bits(state):
    castling = ''
    if (state & (1 << position.bits_castle_K)) > 0:
        castling += 'K'
    if (state & (1 << position.bits_castle_Q)) > 0:
        castling += 'Q'
    if (state & (1 << position.bits_castle_k)) > 0:
        castling += 'k'
    if (state & (1 << position.bits_castle_q)) > 0:
        castling += 'q'

    start = (state >> position.bits_square_from) & 63
    end = (state >> position.bits_square_to) & 63
    status = 'Last move {} to {}. '.format(
            position.Square(start).symbol,
            position.Square(end).symbol)

    if castling == '':
        return status + 'No castling rights.'
    else:
        return status + 'Can castle: ' + castling

def print_board(state, white = '.', black = ' ', size = 2, out = sys.stdout):
    board = display_board(state, white, black, size)
    for row in board:
        out.write((' ' * 8) + row + '\n')
    out.write('\n')
    out.flush()

def print_all(state, white = '.', black = ' ', size = 2, out = sys.stdout):
    print_board(state, white, black, size)
    out.write(display_extra_bits(state) + '\n\n')
    out.flush()

if __name__ == "__main__":
    state = int(sys.argv[1])
    print_all(state)
