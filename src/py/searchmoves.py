import position
import moves

#
# All functions take the current state as an argument
#
#   illegal_check       Can the current player capture the enemy king
#   in_check            Is the current player in check
#   legal_moves         List of all moves legal from current position
#   legal_responses     List of all legal successor states from current position
#   legal_responses_no_check    List of all legal successor states from
#                       current position, including illegally entering check
#

_am = moves.allmoves.moves

_l64_16 = lambda : [[[] for i in range(16)] for j in range(64)]
_l64 = lambda : [[] for j in range(64)]
_l2_64_16 = lambda : {True : _l64_16(), False : _l64_16()}
_l2_64 = lambda : {True : _l64(), False : _l64()}

_mask = position.mask_square_low
_L = position.bits_square

class CastleMove:
    def __init__(self, kingside, white):
        self.white = white
        move, inbetweens = moves.Move.castle(kingside, white)
        self.move = move
        a, b = move.get4()[:2]
        c, d, e = self.potential_captures(inbetweens[0])
        f, g, h = self.potential_captures(inbetweens[1])
        self.legality = (a, b, c, d, e, f, g, h)

    def potential_captures(self, partial_move):
        captures = []
        for move in _am:
            if move.capture and (move.white != self.white) and (move.end == partial_move.end):
                a, b, c, d = move.get4()
                captures.append((a, b))
        return (partial_move.get4()[2], partial_move.get4()[3], captures)

    def is_legal(self, state):
        a, b, c, d, e, f, g, h = self.legality
        if state & a != b:
            return False

        s = ((state & c) | d)
        for x, y in e:
            if (s & x) == y:
                return False

        s = ((state & f) | g)
        for x, y in h:
            if (s & x) == y:
                return False

        return True

class Castles:
    def __init__(self):
        self.castles = [
                    CastleMove(False, False),
                    CastleMove(False, True),
                    CastleMove(True, False),
                    CastleMove(True, True)
                ]

    def search(self, state):
        ms = []
        for castle in self.castles:
            if castle.is_legal(state):
                ms.append(castle.move)
        return ms

castles = Castles().search

class RegMoves:
    def __init__(self):
        self.moves = _l2_64_16()
        for move in _am:
            white = move.white
            piece = move.piece.bits(white) & _mask
            self.moves[white][move.start][piece].append(move)

    def search(self, state):
        white = position.white_turn(state)

        m = self.moves[white]

        ms = []
        s = state & position.mask_board
        for i in range(64):
            for move in m[i][s & _mask]:
                if move.is_legal(state):
                    ms.append(move)
            s = s >> _L
        return ms

regular_moves = RegMoves().search

class RegMovesFast:
    def __init__(self):
        self.moves = _l2_64_16()
        for move in _am:
            white = move.white
            piece = move.piece.bits(white) & _mask
            self.moves[white][move.start][piece].append(move.get4())

    def search(self, state):
        white = position.white_turn(state)

        m = self.moves[white]

        ns = []
        s = state & position.mask_board
        for i in range(64):
            for a, b, c, d in m[i][s & _mask]:
                if (state & a) == b:
                    ns.append((state & c) | d)
            s = s >> _L
        return ns

regular_moves_fast = RegMovesFast().search

class VerifyCheck:
    def __init__(self):
        self.captures_rev = _l2_64()
        for move in _am:
            if move.piece is position.king:
                continue
            if move.capture:
                a, b, c, d = move.get4()
                self.captures_rev[move.white][move.end].append((a, b))

    def illegal_check(self, state):
        white = position.white_turn(state)

        ms = self.captures_rev[white]

        k = position.king.bits(not white) & _mask

        s = state & position.mask_board
        for i in range(64):
            if (s & _mask) == k:
                for a, b in ms[i]:
                    if (state & a) == b:
                        return True
            s = s >> _L
        return False

    def in_check(self, state):
        white = position.white_turn(state)
        return self.illegal_check(moves.Move.pass_turn(white).apply(state))

_vc = VerifyCheck()
illegal_check = _vc.illegal_check
in_check = _vc.in_check

def legal_moves_no_check(state):
    return castles(state) + regular_moves(state)

def legal_moves(state):
    ms = []
    for move in legal_moves_no_check(state):
        if not illegal_check(move.apply(state)):
            ms.append(move)
    return ms

def legal_responses_no_check(state):
    ns = regular_moves_fast(state)
    for move in castles(state):
        ns.append(move.apply(state))
    return ns

def legal_responses(state):
    ns = []
    for n in regular_moves_fast(state):
        if not illegal_check(n):
            ns.append(n)
    for move in castles(state):
        n = move.apply(state)
        if not illegal_check(n):
            ns.append(n)
    return ns
