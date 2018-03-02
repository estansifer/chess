import core.position as pos
import core.moves
import cstate
import clegalmoves

allmoves = core.moves.allmoves.moves

#
# Stores all legal moves of the specified color, including castle moves.
# Also stores legal opposing moves that could capture this color's king,
# for the purpose of testing legality of moves.
#
class MovesOneColor:
    def __init__(self, white):
        self.white = white
        self.init_check()
        self.init_castles()
        self.init_moves()

    def init_check(self):
        # For each square, create a list of all possible moves the opponent
        # could make that involves capturing a king on that square.
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
        self.castle_king = self.init_castle(True)
        self.castle_queen = self.init_castle(False)

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

    def legalmoves(self, state):
        result = []

        for move in allmoves:
            if move.is_legal(state):
                new_state = move.apply(state)
                if not self.illegal_check(new_state):
                    result.append(move)

        if self.white.castle_king.is_legal(state):
            result.append(core.moves.Move.castle(True, True)[0])
        if self.white.castle_queen.is_legal(state):
            result.append(core.moves.Move.castle(False, True)[0])
        if self.black.castle_king.is_legal(state):
            result.append(core.moves.Move.castle(True, False)[0])
        if self.black.castle_queen.is_legal(state):
            result.append(core.moves.Move.castle(False, False)[0])

        return result

    def illegal_check(self, state):
        if pos.white_turn(state):
            check = self.black.check
        else:
            check = self.white.check
        check.set_state_py(state)
        return check.illegal_check()

    def in_check(self, state):
        if pos.white_turn(state):
            check = self.white.check
        else:
            check = self.black.check
        check.set_state_py(state)
        return check.in_check()

moves = Moves()
