#
# State
#   Represented as a bit string. Most-to-least significant order below.
#   Position history is not represented.
#
#   # bits  meaning
#   8       files (a-h) where a pawn double-moved last turn
#   1       white can castle queenside
#   1       white can castle kingside
#   1       black can castle queenside
#   1       black can castle kingside
#   1       a pawn was moved last turn
#   1       a piece was captured last turn
#   1       white to play
#   64 x 5  board state
#
#   Squares are numbered 0 to 63
#   A1 0
#   B1 1
#   H1 7
#   A2 8
#   H8 63

bits_piece_size         = 3
bits_white_piece        = 0b10000
bits_black_piece        = 0b01000

bits_a1                 = 0
bits_square_size        = 5
bits_square_mask        = (1 << bits_square_size) - 1
bits_square_low_mask    = (1 << 4) - 1
bits_piece_mask         = (1 << 3) - 1
bits_file_inc           = bits_square_size
bits_row_inc            = bits_file_inc * 8
bits_board_size         = bits_row_inc * 8
bits_board_mask         = (1 << bits_board_size) - 1

bits_white_turn         = bits_board_size
bits_captured           = bits_white_turn + 1
bits_pawn_moved         = bits_captured + 1
bits_castle_black_king  = bits_pawn_moved + 1
bits_castle_black_queen = bits_castle_black_king + 1
bits_castle_white_king  = bits_castle_black_queen + 1
bits_castle_white_queen = bits_castle_white_king + 1
bits_square_from        = bits_castle_white_queen + 1
bits_square_to          = bits_square_from + 6
bits_state_size         = bits_square_to + 6
bits_state_mask         = (1 << bits_state_size) - 1

# technically also need to check for en passant:
bits_repition_mask      = (bits_board_mask |
        (1 << bits_white_turn) | (0b1111 << bits_castle_black_king))

class Square:
    def __init__(self, number):
        self.number = number # 0 to 63
        self.bits = bits_a1 + bits_square_size * number
        self.symbol = 'abcdefgh'[number % 8] + '12345678'[number // 8]

    def by_symbol(symbol):
        return Square((int(symbol[1]) - 1) * 8 + ord(symbol[0].lower()) - ord('a'))

class Piece:
    def __init__(self, name, symbol, number):
        self.name = name
        self.symbol = symbol
        self.number = number

    def bits(self, white = None):
        if white is None:
            return self.number
        if white:
            return self.number + bits_white_piece
        else:
            return self.number + bits_black_piece

    def display(self, white):
        if white:
            return self.symbol.upper()
        else:
            return self.symbol.lower()

king = Piece('king', 'K', 1)
queen = Piece('queen', 'Q', 2)
rook = Piece('rook', 'R', 3)
bishop = Piece('bishop', 'B', 4)
knight = Piece('knight', 'N', 5)
pawn = Piece('pawn', 'P', 6)

class Move:
    def __init__(self, name = 'No name move'):
        # Move is legal if (state & check_mask) == check_result
        # New board state is (state & (bits_state_mask - set_zero)) | set_one
        self.check_mask = 0
        self.check_result = 0
        self.set_zero = 0
        self.set_one = 0
        self.piece = None
        self.start = None
        self.end = None
        self.capture = None
        self.white = None
        self.name = name

    def check(self, bit, one):
        if (one == 1) or (one is True):
            self.check1(bit)
        else:
            self.check0(bit)

    def check0(self, bit):
        self.check_mask     |= 1 << bit
        self.check_result   &= ~(1 << bit)

    def check1(self, bit):
        self.check_mask     |= 1 << bit
        self.check_result   |= 1 << bit

    def check_bits(self, index, length, bits):
        mask = ((1 << length) - 1) << index
        bits = (bits << index) & mask
        self.check_mask     |= mask
        self.check_result   = (self.check_result & (~mask)) | bits

    def set(self, bit, one):
        if (one == 1) or (one is True):
            self.set1(bit)
        else:
            self.set0(bit)

    def set0(self, bit):
        self.set_zero   |= 1 << bit
        self.set_one    &= ~(1 << bit)

    def set1(self, bit):
        self.set_zero   &= ~(1 << bit)
        self.set_one    |= 1 << bit

    def set_bits(self, index, length, bits):
        mask = ((1 << length) - 1) << index
        bits = (bits << index) & mask
        self.set_zero       |= mask - bits
        self.set_one        |= bits

    def set_capture(self, capture):
        self.set(bits_captured, capture)
        self.capture = capture
        return self

    # piece -- which piece is moving
    # start -- which square moving from
    # end   -- to
    # capture -- is an enemy piece captured?
    # jump  -- do we not require the path to the enemy piece to be clear of pieces?
    def basic_move(piece, start, end, white, capture, jump = False):
        if type(start) is int:
            start = Square(start)
        if type(end) is int:
            end = Square(end)

        name = piece.symbol + start.symbol
        if capture:
            name += 'x'
        else:
            name += ' '
        name += end.symbol

        self = Move(name)
        self.set_capture(capture)
        self.piece = piece
        self.start = start.number
        self.end = end.number
        self.white = white

        # Change turn
        self.check(bits_white_turn, white)
        self.set(bits_white_turn, not white)

        # Pawn moved?
        self.set(bits_pawn_moved, piece is pawn)

        # Castle rights?
        sn = start.number
        en = end.number
        if (sn == 60) or (en == 60) or (sn == 63) or (en == 63):
            self.set0(bits_castle_black_king)
        if (sn == 60) or (en == 60) or (sn == 56) or (en == 56):
            self.set0(bits_castle_black_queen)
        if (sn == 4) or (en == 4) or (sn == 7) or (en == 7):
            self.set0(bits_castle_white_king)
        if (sn == 4) or (en == 4) or (sn == 0) or (en == 0):
            self.set0(bits_castle_white_queen)

        # Does piece exist at correct square?
        sb = start.bits
        eb = end.bits
        cp = piece.bits(white)
        self.check_bits(sb, bits_square_size, cp)

        # Does target have correct square?
        if capture:
            if white:
                self.check_bits(eb + 3, 2, 0b01)
            else:
                self.check_bits(eb + 3, 2, 0b10)
        else:
            self.check_bits(eb, bits_square_size, 0)

        # Track squares moved
        self.set_bits(bits_square_from, 6, sn)
        self.set_bits(bits_square_to, 6, en)
        self.set_bits(sb, bits_square_size, 0)
        self.set_bits(eb, bits_square_size, cp)

        # Is path clear?
        if not jump:
            k = abs(sn - en)
            if k % 8 == 0:
                if en > sn:
                    step = 8
                else:
                    step = -8
            elif k % 9 == 0:
                if en > sn:
                    step = 9
                else:
                    step = -9
            elif (sn // 8) == (en // 8):
                if en > sn:
                    step = 1
                else:
                    step = -1
            elif k % 7 == 0:
                if en > sn:
                    step = 7
                else:
                    step = -7
            else:
                step = None

            if step is not None:
                for i in range(sn + step, en, step):
                    self.check_bits(Square(i).bits, bits_square_size, 0)

        return self

    def en_passant(start, end, white):
        self = Move.basic_move(pawn, start, end, white, False, True)
        self.name += ' ep'

        if white:
            target = end - 8
        else:
            target = end + 8

        self.check_bits(Square(target).bits, bits_square_size, pawn.bits(not white))
        self.check_bits(bits_square_from, 6, 2 * end - target)
        self.check_bits(bits_square_to, 6, target)

        self.set_capture(True)
        self.set_bits(Square(target).bits, bits_square_size, 0)
        return self

    def promote(start, end, white, capture, new_piece):
        self = Move.basic_move(pawn, start, end, white, capture, True)
        self.name += ' =' + new_piece.symbol
        self.set_bits(Square(end).bits, bits_square_size, new_piece.bits(white))
        return self

    def null():
        return Move('null')

    def pass_turn(white):
        self = Move('pass')

        self.check(bits_white_turn, white)
        self.set(bits_white_turn, not white)
        self.set_capture(False)
        self.white = white
        return self

    # returns (move, [list of positions to check for check])
    def castle(kingside, white):
        a = 4
        if kingside:
            name = 'O-O'
            b = 7
            c = 1
        else:
            name = 'O-O-O'
            b = 0
            c = -1

        if not white:
            a += 56
            b += 56

        self = Move.basic_move(king, a, a + 2 * c, white, False, False)
        self.name = name

        if kingside:
            if white:
                self.check1(bits_castle_white_king)
            else:
                self.check1(bits_castle_black_king)
        else:
            self.check_bits(Square(a - 3).bits, bits_square_size, 0)
            if white:
                self.check1(bits_castle_white_queen)
            else:
                self.check1(bits_castle_black_queen)

        self.check_bits(Square(b).bits, bits_square_size, rook.bits(white))
        self.set_bits(Square(b).bits, bits_square_size, 0)
        self.set_bits(Square(a + c).bits, bits_square_size, rook.bits(white))

        inbetweens = [
                Move.pass_turn(white),
                Move.basic_move(king, a, a + c, white, False, False)
            ]

        return (self, inbetweens)

    def remove_piece(square):
        if type(square) is int:
            square = Square(square)
        self = Move('x' + square.symbol)
        self.set_bits(square.bits, bits_square_size, 0)
        return self

    def place_piece(square, piece, white):
        if type(square) is int:
            square = Square(square)
        self = Move(square.symbol + '=' + piece.display(white))
        self.check_bits(square.bits, bits_square_size, 0)
        self.set_bits(square.bits, bits_square_size, piece.bits(white))
        return self

    def is_legal(self, state):
        return (state & self.check_mask) == self.check_result

    def apply(self, state):
        return (state & (~self.set_zero)) | self.set_one

    def get4(self):
        return (self.check_mask, self.check_result, ~self.set_zero, self.set_one)

class Moves:
    def __init__(self):
        l64_16 = lambda : [[[] for i in range(16)] for j in range(64)]
        l64 = lambda : [[] for j in range(64)]
        self.all_moves = []
        self.moves = {
                True : l64_16(),
                False : l64_16()
            }
        self.captures = {
                True : l64_16(),
                False : l64_16()
            }
        self.captures_rev = {
                True : l64(),
                False : l64()
            }
        self.castles = []
        self.add_piece_moves()
        self.add_pawn_moves()
        self.add_castles()

    def add_move(self, move):
        white = move.white
        self.all_moves.append(move)
        p = move.piece.bits(white) & bits_square_low_mask
        self.moves[white][move.start][p].append(move)
        if move.capture:
            self.captures[white][move.start][p].append(move)
            self.captures_rev[white][move.end].append(move)

    def add_reg_moves(self, piece, start, end):
        self.add_move(Move.basic_move(piece, start, end, True, False))
        self.add_move(Move.basic_move(piece, start, end, True, True))
        self.add_move(Move.basic_move(piece, start, end, False, False))
        self.add_move(Move.basic_move(piece, start, end, False, True))

    def add_in_bounds(self, piece, row, col, dxy):
        for dx, dy in dxy:
            if dx == 0 and dy == 0:
                continue
            a = row + dx
            b = col + dy
            if 0 <= a and a < 8 and 0 <= b and b < 8:
                self.add_reg_moves(piece, row * 8 + col, a * 8 + b)

    def add_piece_moves(self):
        rank = list(range(-7, 8))
        movement_rook = [[i, 0] for i in rank] + [[0, i] for i in rank]
        movement_bishop = [[i, i] for i in rank] + [[i, -i] for i in rank]
        movement_queen = movement_rook + movement_bishop
        movement_king = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
        movement_knight = [[-2, -1], [-2, 1], [2, -1], [2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2]]

        for i in range(8):
            for j in range(8):
                self.add_in_bounds(king, i, j, movement_king)
                self.add_in_bounds(queen, i, j, movement_queen)
                self.add_in_bounds(rook, i, j, movement_rook)
                self.add_in_bounds(bishop, i, j, movement_bishop)
                self.add_in_bounds(knight, i, j, movement_knight)

    def add_pawn_moves(self):
        p = pawn

        add = self.add_move
        promos = [queen, rook, bishop, knight]
        for i in range(1, 7):
            for j in range(8):
                a = i * 8 + j

                if i < 6:
                    add(Move.basic_move(p, a, a + 8, True, False))
                else:
                    add(Move.basic_move(p, a, a - 16, False, False))
                    for new in promos:
                        add(Move.promote(a, a + 8, True, False, new))

                if i > 1:
                    add(Move.basic_move(p, a, a - 8, False, False))
                else:
                    add(Move.basic_move(p, a, a + 16, True, False))
                    for new in promos:
                        add(Move.promote(a, a + 8, False, False, new))

                if j > 0:
                    if i < 6:
                        add(Move.basic_move(p, a, a + 7, True, True))
                    else:
                        for new in promos:
                            add(Move.promote(a, a + 7, True, True, new))


                    if i > 1:
                        add(Move.basic_move(p, a, a - 9, False, True))
                    else:
                        for new in promos:
                            add(Move.promote(a, a - 9, False, True, new))

                    if i == 4:
                        add(Move.en_passant(a, a + 7, True))
                    if i == 3:
                        add(Move.en_passant(a, a - 9, False))

                if j < 7:
                    if i < 6:
                        add(Move.basic_move(p, a, a + 9, True, True))
                    else:
                        for new in promos:
                            add(Move.promote(a, a + 9, True, True, new))


                    if i > 1:
                        add(Move.basic_move(p, a, a - 7, False, True))
                    else:
                        for new in promos:
                            add(Move.promote(a, a - 7, False, True, new))

                    if i == 4:
                        add(Move.en_passant(a, a + 9, True))
                    if i == 3:
                        add(Move.en_passant(a, a - 7, False))

    def add_castles(self):
        self.castles.append(Move.castle(False, False))
        self.castles.append(Move.castle(False, True))
        self.castles.append(Move.castle(True, False))
        self.castles.append(Move.castle(True, True))

    # Determines whether the opponent played into check
    def illegal_check(self, state):
        white = (state & (1 << bits_white_turn)) > 0

        s = state & bits_board_mask
        for i in range(64):
            if (s & bits_square_mask) == king.bits(not white):
                for move in self.captures_rev[white][i]:
                    if move.is_legal(state):
                        return True
            s = s >> bits_square_size
        return False

    def legal_moves_no_castle_check(self, state):
        white = (state & (1 << bits_white_turn)) > 0

        m = self.moves[white]

        moves = []
        s = state & bits_board_mask
        for i in range(64):
            for move in m[i][s & bits_square_low_mask]:
                if move.is_legal(state):
                    moves.append(move)
            s = s >> bits_square_size
        return moves

    def legal_captures_no_check(self, state):
        white = (state & (1 << bits_white_turn)) > 0

        m = self.captures[white]

        moves = []
        s = state & bits_board_mask
        for i in range(64):
            for move in m[i][s & bits_square_low_mask]:
                if move.is_legal(state):
                    moves.append(move)
            s = s >> bits_square_size
        return moves

    def legal_castles_no_check(self, state):
        white = (state & (1 << bits_white_turn)) > 0

        moves = []
        for move, inbetweens in self.castles:
            if move.is_legal(state):
                for move0 in inbetweens:
                    s = move0.apply(state)
                    if self.illegal_check(s):
                        break
                else:
                    moves.append(move)
        return moves

    def legal_moves_no_check(self, state):
        return self.legal_moves_no_castle_check(state) + self.legal_castles_no_check(state)

    def legal_moves(self, state):
        moves = []
        for move in self.legal_moves_no_check(state):
            if not self.illegal_check(move.apply(state)):
                moves.append(move)
        return moves

    def in_check(self, state):
        white = (state & (1 << bits_white_turn)) > 0
        return self.illegal_check(Move.pass_turn(white).apply(state))

def initial_state():
    s = [((1 << bits_white_turn) +
        (1 << bits_castle_black_king) +
        (1 << bits_castle_black_queen) +
        (1 << bits_castle_white_king) +
        (1 << bits_castle_white_queen))]

    def place_piece(square, piece, white):
        bsq = Square(square).bits
        s[0] = (s[0] & (~(bits_square_mask << bsq))) | (piece.bits(white) << bsq)

    place_piece( 0, rook  , True )
    place_piece( 1, knight, True )
    place_piece( 2, bishop, True )
    place_piece( 3, queen , True )
    place_piece( 4, king  , True )
    place_piece( 5, bishop, True )
    place_piece( 6, knight, True )
    place_piece( 7, rook  , True )
    place_piece( 8, pawn  , True )
    place_piece( 9, pawn  , True )
    place_piece(10, pawn  , True )
    place_piece(11, pawn  , True )
    place_piece(12, pawn  , True )
    place_piece(13, pawn  , True )
    place_piece(14, pawn  , True )
    place_piece(15, pawn  , True )

    place_piece(48, pawn  , False)
    place_piece(49, pawn  , False)
    place_piece(50, pawn  , False)
    place_piece(51, pawn  , False)
    place_piece(52, pawn  , False)
    place_piece(53, pawn  , False)
    place_piece(54, pawn  , False)
    place_piece(55, pawn  , False)
    place_piece(56, rook  , False)
    place_piece(57, knight, False)
    place_piece(58, bishop, False)
    place_piece(59, queen , False)
    place_piece(60, king  , False)
    place_piece(61, bishop, False)
    place_piece(62, knight, False)
    place_piece(63, rook  , False)
    return s[0]
