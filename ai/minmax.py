import random
import ai.treesearch
import ai.gametree
import ai.evaluator
import position
import searchmoves
import time

class AIGreedy:
    def __init__(self, white, flateval, searcheval, name):
        self.white = white
        self.flateval = flateval
        self.name = name
        self.tree = ai.gametree.GameTree()
        self.tree.set_flatevaluator(flateval)
        self.searcheval = searcheval(self.tree).value
        self.total_time = 0

    def choose_move(self, gs):
        start = time.process_time()

        state = gs.state
        self.searcheval(state = state, turn = gs.turn)

        h = self.tree.hashstate(state)
        node = self.tree.cache[h]
        if node[2] is None:
            self.tree.expand_children(h)

        print("Current board value: ", node[3])

        best_move = None
        if self.white:
            best_value = -(10 ** 9)
            better = lambda a, b : a > b
        else:
            best_value = 10 ** 9
            better = lambda a, b : a < b

        moves = searchmoves.legal_moves(state)
        random.shuffle(moves)
        for move in moves:
            value = self.tree.lookup(move.apply(state))[3]
            if better(value, best_value):
                best_value = value
                best_move = move

        end = time.process_time()
        self.total_time += (end - start)

        return best_move

    def game_over(self, game):
        print("Nodes searched in game tree: ", len(self.tree.cache))
        print("Total time used (s): ", self.total_time)
        print("Time per node (us): ", 1000000 * self.total_time / (len(self.tree.cache) + 1))

def ai_minmax(white):
    flateval = ai.evaluator.SumPiece.from_file(0)
    return AIGreedy(
            white,
            flateval.value,
            ai.treesearch.MinMax,
            'AI_MinMax_3_S_0'
        )

def ai_minmax_quiescent(white):
    flateval = ai.evaluator.SumPiece.from_file(0)
    return AIGreedy(
            white,
            flateval.value,
            ai.treesearch.MinMaxQuiescent,
            'AI_MinMaxQuiescent_3_6_S_0'
        )
