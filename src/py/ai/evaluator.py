# Heuristic game state evaluators that do not use any look ahead
# or game tree exploration. More sophisticated evaluators are
# built off of these.
#
# An evaluator returns a pair of (value, evaluation quality).
#
# Evaluators:
#   SumPiece.from_file().value
#   game_over_value

import os
import os.path
import json
import sys

import position
import moves
import searchmoves
import cevaluator
import legalmoves

def filename(category, index):
    return os.path.join(os.path.dirname(sys.argv[0]), '..', '..',
            'params', category, '{:04d}'.format(index))

def read_params(fn):
    with open(fn, 'r') as f:
        j = json.load(f)
        return j

def write_params(fn, p):
    os.makedirs(os.path.dirname(fn), exist_ok = True)
    with open(fn, 'w') as f:
        json.dump(p, f, indent = 1)

def from_file(cls, index = 0):
    return cls(read_params(filename(cls.category, index)))

def to_file(e, index = 0):
    write_params(filename(e.category, index), e.params)

class CEval1:
    category = 'eval1'
    def __init__(self, params = None):
        if params is None:
            params = CEval1.default_params()
        self.params = params
        self.prep()

    def default_params():
        values = {}
        values['king'] = [10 ** 6] * 64

        reg_pieces = [
                    (position.bishop, 320, 0.15),
                    (position.knight, 300, 0.15),
                    (position.rook, 500, 0.05),
                    (position.queen, 900, 0.01)
                ]

        move_counts = {}
        for piece, a, b in reg_pieces:
            move_counts[piece.name] = [0] * 64

        for move in moves.allmoves.moves:
            if (move.piece.name in move_counts) and move.white:
                move_counts[move.piece.name][move.start] += 1

        for piece, a, b in reg_pieces:
            least = 99999
            most = 0
            for i in range(64):
                least = min(least, move_counts[piece.name][i])
                most = max(most, move_counts[piece.name][i])

            values[piece.name] = [0] * 64
            for i in range(64):
                k = move_counts[piece.name][i]
                if most == least:
                    v = a
                else:
                    v = a + a * b * (k - least) / (most - least)
                values[piece.name][i] = int(v)

        pcolmult = [1.00, 1.10, 1.20, 1.30, 1.30, 1.20, 1.10, 1.00]
        prowmult = [1.00, 1.00, 1.10, 1.25, 1.45, 1.90, 2.50, 1.00]
        for i in range(8):
            for j in range(8):
                values['pawn'][j * 8 + i] = int(100 * pcolmult[i] * prowmult[j])

        return values

    def prep(self):
        values = [[0 for j in range(16)] for i in range(64)]
        for piece in position.pieces:
            for row in range(8):
                for col in range(8):
                    i = row * 8 + col
                    i_ = (7 - row) * 8 + col
                    v = self.params[piece.name][i]
                    values[i][piece.bits(True) & 0b1111] = v
                    values[i_][piece.bits(False) & 0b1111] = v

        self.ceval = cevaluator.Eval1(values)

    def evaluate(self, tree, n):
        self.ceval.evaluate(tree.tree, n)

class GameOverEval:
    # Should only be called if the specified node has no child nodes (i.e., no legal moves)
    def evaluate(self, tree, n):
        t = tree.tree
        if t.child(n) == -2:
            if tree.in_check(n):
                if t.turn(n) % 2 == 0:
                    t.set_value(n, 10 ** 8, 10 ** 8)
                else:
                    t.set_value(n, -(10 ** 8), 10 ** 8)
            t.set_value(n, 0, 10 ** 8)

gameover = GameOverEval()
