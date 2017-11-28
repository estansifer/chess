import random
import position
import searchmoves
import ai.evaluator

mask = position.mask_square
L = position.bits_square
legal_moves = searchmoves.legal_moves
legal_responses = searchmoves.legal_responses

#
# Attributes stored at each node:
#   [
#       0   state
#       1   turn number
#       2   list of hashes of child states
#       3   evaluation
#       4   evaluation quality
#   ]
#
#   2 is None until children of this node have not been explored yet
#   3 is floating point number
#   4 is integer
#
#
#   evaluation quality = 0 if unevaluated
#       = a * 10^6 + b * 10^4 + c otherwise,
#       where a = 1 if the evaluation is recursive and a = 0 otherwise
#       b = evaluator type
#       c = parameter specific to the evaluator, typically depth
#
class GameTree:
    def __init__(self):
        self.cache = {}
        self.flateval = lambda state : (0, 0)

    def set_flatevaluator(self, flateval):
        self.flateval = flateval

    def clearcache(self):
        self.cache = {}

    def rerootcache(self, state):
        newcache = {}
        stack = [hash(state)]
        while len(stack) > 0:
            h = stack.pop()
            node = self.cache.get(h)
            if not (node is None):
                newcache[h] = node
                if not (node[2] is None):
                    stack.extend(node[2])
        print("Reduced cache from {} to {}".format(len(self.cache), len(newcache)))
        self.cache = newcache

    def lookup(self, state):
        return self.lookup_hash(hash(state))

    def lookup_hash(self, h):
        return self.cache.get(h, None)

    def expand_children(self, h):
        parent = self.cache[h]
        if parent[2] is None:
            turn = parent[1] + 1
            children = legal_responses(parent[0])
            children_hash = []
            for s in children:
                h2 = hash(s)
                children_hash.append(h2)
                if h2 not in self.cache:
                    e, q = self.flateval(state = s, turn = turn)
                    self.cache[h2] = [
                            s,
                            turn,
                            None,
                            e,
                            q
                        ]
            parent[2] = children_hash

            # if len(children) == 0:
                # e, q = ai.evaluator.game_over_value(parent[0])
                # parent[3] = e
                # parent[4] = q
        return parent

    def insert_node(self, state, turn):
        h = hash(state)
        if h not in self.cache:
            e, q = self.flateval(state)
            self.cache[h] = [
                    state,
                    turn,
                    None,
                    e,
                    q
                ]
