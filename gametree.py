import random
import position

hashlength = 50
def rhash():
    return random.randint(0, (1 << hashlength) - 1)

hashes = [[rhash() for i in range(32)] for j in range(64)]

def hashstate(state):
    result = 0

    for i in range(64):
        result ^= hashes[i][state & position.bits_square_mask]
        state = state >> position.bits_square_size
    return result ^ state

# Stores a mapping from hashed state to:
#   [state, list of hashes of child states, evaluation, evaluation quality]
class GameTree:
    def __init__(self):
        self.cache = {}

    def lookup(self, state):
        return self.lookup_hash(hashstate(state))

    def lookup_hash(self, h):
        return self.cache.get(h, None)

    def set(self, state):
        h = hashstate(state)
        if h not in self.cache:
            self.cache[h] = [state, None, None, 0]
        return self.cache[h]
