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
import searchmoves

L = position.bits_square_size
K = 1 << L
mask = K - 1

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

class SumPiece:
    category = 'piece'
    def __init__(self, params):
        self.params = params
        self.prep()
        self.name = 'P'

    def default():
        return SumPiece({
                'king' : 10 ** 6,
                'queen' : 9,
                'rook' : 5,
                'bishop' : 3.2,
                'knight' : 3,
                'pawn' : 1
            })

    def from_file(index = 0):
        return from_file(SumPiece, index)

    def to_file(self, index = 0):
        to_file(self, index)

    def prep(self):
        self.values = [0] * K
        for piece in position.pieces:
            self.values[piece.bits(True)] = self.params[piece.name]
            self.values[piece.bits(False)] = -self.params[piece.name]

    def value(self, state, turn = None):
        v = 0
        for i in range(64):
            v += self.values[state & mask]
            state = state >> L
        return (v, 1)

# Given that the current player has no legal moves, determine the outcome of the game
def game_over_value(state, turn = None):
    if searchmoves.in_check(state):
        if (state & (1 << position.bits_white_turn)) > 0:
            return (-(10 ** 9), 10 ** 9)
        else:
            return (10 ** 9, 10 ** 9)
    else:
        return (0, 10 ** 9)
