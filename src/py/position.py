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
bits_repitition_mask    = (bits_board_mask |
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
pieces = [king, queen, rook, bishop, knight, pawn]

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
