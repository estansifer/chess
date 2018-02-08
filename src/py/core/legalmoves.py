import core.position as pos
import core.moves
import cstate
import clegalmoves

allmoves = core.moves.allmoves.moves

class MovesOneColor:
    def __init__(self, white):
        self.white = white
        self.init_check()
        self.init_castles()
        self.init_moves()

    def init_check(self):
        # For each square, create a list of all possible moves the opponent
        # could make that involves capturing a king on each given square.
        # Note that king-king captures need never be considered.
        self.captures_rev = [[] for i in range(64)]

        for move in allmoves:
            if move.capture and (not (move.piece is pos.king)) and (move.white != self.white):
                a, b, c, d = move.get4()
                self.captures_rev[move.end].append((a, b))

        if self.white:
            bits_king = pos.bits_king_white
        else:
            bits_king = pos.bits_king_black

        self.check = clegalmoves.Check(self.captures_rev, bits_king, pos.bits_turn)

    def init_castles(self):
        self.castle_king = self.init_castle(self, True)
        self.castle_queen = self.init_castle(self, True)

    def init_castle(self, kingside):
        castle, inbetweens = core.moves.Move.castle(kingside, self.white)
        move1 = clegalmoves.MoveNoCheck(castle.get4(), self.captures_rev[castle.end])
        move2 = clegalmoves.MoveNoCheck(inbetweens[0].get4(), self.captures_rev[inbetweens[0].end])
        move3 = clegalmoves.MoveNoCheck(inbetweens[1].get4(), self.captures_rev[inbetweens[1].end])

        return clegalmoves.CastleMove(move1, move2, move3)

    def init_moves(self):
        moves = [[[] for j in range(16)] for i in range(64)]

        for move in allmoves:
            if move.white == self.white:
                moves[move.start][move.piece.bits(self.white) & 0b1111].append(move.get4())

        self.moves = clegalmoves.LegalMoves(moves, self.check, self.castle_king, self.castle_queen)

class Moves:
    def __init__(self):
        self.white = MovesOneColor(True)
        self.black = MovesOneColor(False)

moves = Moves()
