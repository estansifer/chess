import random
import time

import ai.treesearch
import ai.gametree
import ai.evaluator
import core.position
import core.moves
import core.legalmoves

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
        self.evaluator.evaluate(self.tree, n)

        print("Current board value: ", t.value(n))

        best_value = 10 ** 9
        best_move = core.moves.Move.resign()

        ms = core.legalmoves.moves.legalmoves(gs.state)
        random.shuffle(ms)
        for move in ms:
            k = t.find_state(move.apply(gs.state), gs.turn + 1)
            if k >= 0:
                value = t.value(k)
                if value < best_value:
                    best_value = value
                    best_move = move

        end = time.process_time()
        self.total_time += (end - start)

        print("Nodes examined: ", t.number_nodes(), t.number_nodes() / (end - start))

        return best_move

    def game_over(self, game):
        print("Total time used (s): ", self.total_time)

    def __call__(self, white):
        self.white = white
        return self

flat_eval = ai.evaluator.CEval1()

def ai_minmax(depth = 4):
    return AIGreedy(
            None,
            ai.treesearch.MinMax(flat_eval, depth),
            'AI_MinMax_{}'.format(depth)
        )


def ai_minmax_quiescent(depth = 3, noisy_depth = 8):
    return AIGreedy(
            None,
            ai.treesearch.MinMaxQuiescent(flat_eval, depth, noisy_depth),
            'AI_MinMaxQuiescent_{}_{}'.format(depth, noisy_depth)
        )
