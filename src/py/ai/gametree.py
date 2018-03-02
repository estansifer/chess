import core.position
import core.legalmoves
import cstate
import clegalmoves

class GameTree:
    def __init__(self):
        sl = cstate.StateList(100000, 1.5)
        self.tree = cstate.GameTree(sl, core.position.bits_captured)
        self.moves = core.legalmoves.moves

    def expand_children(self, parent):
        clegalmoves.add_children(self.tree, parent,
                core.legalmoves.moves.white.moves,
                core.legalmoves.moves.black.moves)

    def in_check(self, n):
        if self.tree.turn(n) % 2 == 0:
            check = self.moves.black.check
        else:
            check = self.moves.white.check
        check.set_state(self.tree, n)
        return check.in_check()


def ignore():

    def clear(self):
        self.tree.clear_states()

    def add_state(self, state, turn):
        self.tree.add_state(state, turn)

    def rebase(self, gs):
        self.clear()
        self.add_state(gs.state, gs.turn)

