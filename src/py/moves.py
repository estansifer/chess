from position import *

class Move:
    def __init__(self, name = 'No name move'):
        # Move is legal if (state & check_mask) == check_result
        # New board state is (state & (bits_state_mask - set_zero)) | set_one
        self.check_mask = Z(0)
        self.check_result = Z(0)
        self.set_zero = Z(0)
        self.set_one = Z(0)
        self.piece = None
        self.start = None
        self.end = None
        self.capture = None
        self.white = None
        self.name = name
        self.is_resignation = (name == 'Resign')

    def check(self, bit, one):
        if (one == 1) or (one is True):
            self.check1(bit)
        else:
            self.check0(bit)

    def check0(self, bit):
        self.check_mask     |= Z(1 << bit)
        self.check_result   &= Z(~(1 << bit))

    def check1(self, bit):
        self.check_mask     |= Z(1 << bit)
        self.check_result   |= Z(1 << bit)

    def check_bits(self, index, length, bits):
        mask = Z(((1 << length) - 1) << index)
        bits = Z((bits << index) & mask)
        self.check_mask     |= mask
        self.check_result   = (self.check_result & (~mask)) | bits

    def set(self, bit, one):
        if (one == 1) or (one is True):
            self.set1(bit)
        else:
            self.set0(bit)

    def set0(self, bit):
        self.set_zero   |= Z(1 << bit)
        self.set_one    &= Z(~(1 << bit))

    def set1(self, bit):
        self.set_zero   &= Z(~(1 << bit))
        self.set_one    |= Z(1 << bit)

    def set_bits(self, index, length, bits):
        mask = Z(((1 << length) - 1) << index)
        bits = Z((bits << index) & mask)
        self.set_zero       = (self.set_zero - (self.set_zero & mask)) | (mask - bits)
        self.set_one        = (self.set_one - (self.set_one & mask)) | bits

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
        self.check(bits_turn, white)
        self.set(bits_turn, not white)

        # Pawn moved?
        self.set(bits_pawn_moved, piece is pawn)

        # Castle rights?
        sn = start.number
        en = end.number
        if (sn == 4) or (en == 4) or (sn == 7) or (en == 7):
            self.set0(bits_castle_K)
        if (sn == 4) or (en == 4) or (sn == 0) or (en == 0):
            self.set0(bits_castle_Q)
        if (sn == 60) or (en == 60) or (sn == 63) or (en == 63):
            self.set0(bits_castle_k)
        if (sn == 60) or (en == 60) or (sn == 56) or (en == 56):
            self.set0(bits_castle_q)

        # Does piece exist at correct square?
        sb = start.bits
        eb = end.bits
        cp = piece.bits(white)
        self.check_bits(sb, bits_square, cp)

        # Does target have correct square?
        if capture:
            if white:
                self.check_bits(eb + bits_piece, bits_color, 0b01)
            else:
                self.check_bits(eb + bits_piece, bits_color, 0b10)
        else:
            self.check_bits(eb, bits_square, 0)

        # Track squares moved
        self.set_bits(bits_square_from, 6, sn)
        self.set_bits(bits_square_to, 6, en)
        self.set_bits(sb, bits_square, 0)
        self.set_bits(eb, bits_square, cp)
        if piece is king:
            if white:
                self.set_bits(bits_king_white, 6, en)
            else:
                self.set_bits(bits_king_black, 6, en)

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
                    self.check_bits(Square(i).bits, bits_square, 0)

        return self

    def en_passant(start, end, white):
        self = Move.basic_move(pawn, start, end, white, False, True)
        self.name += ' ep'

        if white:
            target = end - 8
        else:
            target = end + 8

        self.check_bits(bits_square_from, 6, 2 * end - target)
        self.check_bits(bits_square_to, 6, target)

        self.set_capture(True)
        self.check_bits(Square(target).bits, bits_square, pawn.bits(not white))
        self.set_bits(Square(target).bits, bits_square, 0)

        return self

    def promote(start, end, white, capture, new_piece):
        self = Move.basic_move(pawn, start, end, white, capture, True)
        self.name += ' =' + new_piece.symbol
        self.set_bits(Square(end).bits, bits_square, new_piece.bits(white))
        return self

    def null():
        return Move('null')

    def resign():
        return Move('Resign')

    def pass_turn(white):
        self = Move('pass')

        self.check(bits_turn, white)
        self.set(bits_turn, not white)
        self.set_capture(False)
        self.white = white
        return self

    # returns (move, [list of positions to verify for check])
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
                self.check1(bits_castle_K)
            else:
                self.check1(bits_castle_k)
        else:
            self.check_bits(Square(a - 3).bits, bits_square, 0)
            if white:
                self.check1(bits_castle_Q)
            else:
                self.check1(bits_castle_q)

        self.check_bits(Square(b).bits, bits_square, rook.bits(white))
        self.set_bits(Square(b).bits, bits_square, 0)
        self.set_bits(Square(a + c).bits, bits_square, rook.bits(white))

        nomove = Move.pass_turn(white)
        nomove.start = nomove.end = a

        inbetweens = [
                nomove,
                Move.basic_move(king, a, a + c, white, False, False)
            ]

        return (self, inbetweens)

    def remove_piece(square):
        if type(square) is int:
            square = Square(square)
        self = Move('x' + square.symbol)
        self.set_bits(square.bits, bits_square, 0)
        return self

    def place_piece(square, piece, white):
        if type(square) is int:
            square = Square(square)
        self = Move(square.symbol + '=' + piece.display(white))
        self.check_bits(square.bits, bits_square, 0)
        self.set_bits(square.bits, bits_square, piece.bits(white))
        return self

    def is_legal(self, state):
        return (state & self.check_mask) == self.check_result

    def apply(self, state):
        return (state & (~self.set_zero)) | self.set_one

    def get4(self):
        return (self.check_mask, self.check_result, ~self.set_zero, self.set_one)

# Except castling
class BuildMoves:
    def __init__(self):
        self.moves = []
        self.add_piece_moves()
        self.add_pawn_moves()

    def add_move(self, move):
        self.moves.append(move)

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

allmoves = BuildMoves()
