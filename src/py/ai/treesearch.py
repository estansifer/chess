import ai.evaluator
import ai.gametree
import core.position

class MinMax:
    def __init__(self, evaluator, depth = 3):
        self.name = 'MinMax'
        self.evaluator = evaluator
        self.depth = depth

    def evaluate(self, tree, n):
        self.recurse(self, tree, n, self.depth)

    def recurse(self, tree, n, depth):
        if depth == 0:
            self.evaluator(tree, n)
        else:
            tree.expand_children(n)
            t = tree.tree

            c = t.child(n)
            if c == -2:
                ai.evaluator.gameover.evaluate(tree, n)
            else:
                white = (t.turn(n) % 2 == 1)
                if white:
                    best = -(10 ** 9)
                else:
                    best = 10 ** 9

                while c != -1:
                    self.recurse(tree, c, depth - 1)
                    val = t.value(c)
                    if white:
                        best = max(best, val)
                    else:
                        best = min(best, val)
                    c = t.sibling(c)

                t.set_value(n, best, 10000 + depth)

class MinMaxQuiescent:
    def __init__(self, evaluator, depth = 3, noisy_depth = 8):
        self.name = 'MinMaxQuiescent'
        self.evaluator = evaluator
        self.depth = depth
        self.noisy_depth = noisy_depth

    def evaluate(self, tree, n):
        self.thresh1 = tree.tree.turn(n) + self.depth
        self.thresh2 = tree.tree.turn(n) + self.noisy_depth
        self.recurse(self, tree, n)

    def recurse(self, tree, n):
        t = tree.tree
        turn = t.turn(n)
        if (turn >= self.thresh2) or ((turn >= self.thresh1) and (t.noisy(n) == 0)):
            self.evaluator(tree, n)
        else:
            tree.expand_children(n)

            c = t.child(n)
            if c == -2:
                ai.evaluator.gameover.evaluate(tree, n)
            else:
                white = (t.turn(n) % 2 == 1)
                if white:
                    best = -(10 ** 9)
                else:
                    best = 10 ** 9

                while c != -1:
                    self.recurse(tree, c)
                    val = t.value(c)
                    if white:
                        best = max(best, val)
                    else:
                        best = min(best, val)
                    c = t.sibling(c)

                t.set_value(n, best, 20000 + depth)
