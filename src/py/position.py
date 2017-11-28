#
# State
#   Represented as a bit string. Most-to-least significant order below.
#   Position history is not represented.
#
#   Squares are numbered 0 to 63
#   A1 0
#   B1 1
#   H1 7
#   A2 8
#   H8 63

import gmpy2

Z = gmpy2.mpz

# Variables named bits_XXX are indices or lengths of bit fields, and are python ints

bits_piece              = 3 # Number of bits to represent a piece
bits_color              = 2 # Number of bits to represent the color of a piece
bits_square             = bits_piece + bits_color # Number of bits to store the state of a square

bits_board              = bits_square * 64

bits_turn               = bits_board
bits_captured           = bits_turn + 1
bits_pawn_moved         = bits_captured + 1
bits_castle             = bits_pawn_moved + 1
bits_square_from        = bits_castle + 4
bits_square_to          = bits_square_from + 6
bits_king_white         = bits_square_to + 6
bits_king_black         = bits_king_white + 6
bits_biggest            = bits_king_black + 6
bits_state              = bits_biggest + 1

bits_castle_K           = bits_castle
bits_castle_Q           = bits_castle + 1
bits_castle_k           = bits_castle + 2
bits_castle_q           = bits_castle + 3


# Variables named mask_XXX are gmpy2.mpz objects
mask_board              = Z((1 << bits_board) - 1)
mask_state              = Z((1 << bits_state) - 1)

mask_white_piece        = Z(0b10000)
mask_black_piece        = Z(0b01000)

mask_piece              = Z((1 << bits_piece) - 1)
mask_square_low         = Z((1 << 4) - 1)
mask_square             = Z((1 << bits_square) - 1)

mask_turn               = Z(1 << bits_turn)
mask_captured           = Z(1 << bits_captured)
mask_pawn_moved         = Z(1 << bits_pawn_moved)
mask_castle             = Z(0b1111 << bits_castle)
mask_repitition         = mask_board | mask_turn | mask_castle

class Square:
    def __init__(self, number):
        self.number     = Z(number) # 0 to 63
        self.bits       = bits_square * number
        self.symbol     = 'abcdefgh'[number % 8] + '12345678'[number // 8]

    def by_symbol(symbol):
        return Square((int(symbol[1]) - 1) * 8 + ord(symbol[0].lower()) - ord('a'))

class Piece:
    def __init__(self, name, symbol, number):
        self.name       = name
        self.symbol     = symbol
        self.number     = Z(number)

    def bits(self, white = None):
        if white is None:
            return self.number
        if white:
            return self.number | mask_white_piece
        else:
            return self.number | mask_black_piece

    def display(self, white):
        if white:
            return self.symbol.upper()
        else:
            return self.symbol.lower()

king        = Piece('king', 'K', 1)
queen       = Piece('queen', 'Q', 2)
rook        = Piece('rook', 'R', 3)
bishop      = Piece('bishop', 'B', 4)
knight      = Piece('knight', 'N', 5)
pawn        = Piece('pawn', 'P', 6)
pieces      = [king, queen, rook, bishop, knight, pawn]

def white_turn(state):
    return (state & mask_turn) > 0

def captured(state):
    return (state & mask_captured) > 0

def initial_state():
    s = [mask_turn |
            mask_castle |
            (4 << bits_king_white) |
            (60 << bits_king_black) |
            (1 << bits_biggest)]

    def place_piece(square, piece, white):
        s[0] |= (piece.bits(white) << Square(square).bits)

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
    return Z(s[0])
