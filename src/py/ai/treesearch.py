import ai.evaluator
import ai.gametree
import position

class MinMax:
    def __init__(self, tree):
        self.tree = tree
        self.name = 'MinMax'

    def value(self, state, turn, depth = 3):
        h = ai.gametree.hashstate(state)
        if h not in self.tree.cache:
            self.tree.insert_node(state, turn)
        return self.value_hashed(h, turn, depth)

    def value_hashed(self, h, turn, depth = 3):
        node = self.tree.cache[h]

        if depth > 0:
            quality = 1010000 + depth
            if quality > node[4]:
                self.tree.expand_children(h)

                if len(node[2]) > 0:
                    values = []
                    for child in node[2]:
                        e, q = self.value_hashed(child, turn + 1, depth - 1)
                        values.append(e)

                    if (turn % 2) == 0:
                        node[3] = min(values)
                    else:
                        node[3] = max(values)

                    node[4] = quality
                else:
                    e, q = ai.evaluator.game_over_value(node[0])
                    node[3] = e
                    node[4] = q

        return (node[3], node[4])

class MinMaxQuiescent:
    def __init__(self, tree):
        self.tree = tree
        self.name = 'MinMaxQuiescent'

    def value(self, state, turn, depth = 3, noisy_depth = 6):
        h = ai.gametree.hashstate(state)
        if h not in self.tree.cache:
            self.tree.insert_node(state, turn)
        return self.value_hashed(h, turn, depth)

    def value_hashed(self, h, turn, depth = 3, noisy_depth = 6):
        node = self.tree.cache[h]

        noisy = ((node[0] & (1 << position.bits_captured)) > 0)

        if depth > 0 or (noisy and (noisy_depth > 0)):
            quality = 1020000 + depth + 50
            if quality > node[4]:
                self.tree.expand_children(h)

                if len(node[2]) > 0:
                    values = []
                    for child in node[2]:
                        e, q = self.value_hashed(child, turn + 1, depth - 1, noisy_depth - 1)
                        values.append(e)

                    if (turn % 2) == 0:
                        node[3] = min(values)
                    else:
                        node[3] = max(values)

                    node[4] = quality
                else:
                    e, q = ai.evaluator.game_over_value(node[0])
                    node[3] = e
                    node[4] = q

        return (node[3], node[4])
