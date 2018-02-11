import random

import core.legalmoves

class AIRandom:
    def __init__(self, white):
        self.white = white
        self.name = 'AIRandom'

    def choose_move(self, gs):
        return random.choice(core.legalmoves.moves.legalmoves(gs.state))

    def game_over(self, game):
        pass
