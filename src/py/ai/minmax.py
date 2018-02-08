import random
import ai.treesearch
import ai.gametree
import ai.evaluator
import position
import moves
import searchmoves
import time

class AIGreedy:
    def __init__(self, white, evaluator, name):
        self.white = white
        self.name = name
        self.tree = ai.gametree.GameTree()
        self.evaluator = evaluator
        self.total_time = 0

    def choose_move(self, gs):
        start = time.process_time()

        t = self.tree.tree
        t.clear_states()
        n = t.add_state(gs.state, gs.turn)
        self.evaluator(self.tree, n)

        print("Current board value: ", t.value(n))

        best_move = moves.Move.resign()
        if self.white:
            best_value = -(10 ** 9)
            better = lambda a, b : a > b
        else:
            best_value = 10 ** 9
            better = lambda a, b : a < b

        ms = searchmoves.legal_moves(state)
        random.shuffle(ms)
        for move in ms:
            k = t.find_state(move.apply(gs.state), gs.turn + 1)
            if k >= 0:
                value = t.value(k)
                if better(value, best_value):
                    best_value = value
                    best_move = move

        end = time.process_time()
        self.total_time += (end - start)

        print("Nodes examined: ", t.number_nodes())

        return best_move

    def game_over(self, game):
        print("Total time used (s): ", self.total_time)

def ai_minmax(white):
    return AIGreedy(
            white,
            ai.treesearch.MinMax,
            'AI_MinMax_3_S_0'
        )

def ai_minmax_quiescent(white):
    return AIGreedy(
            white,
            ai.treesearch.MinMaxQuiescent,
            'AI_MinMaxQuiescent_3_8_S_0'
        )
