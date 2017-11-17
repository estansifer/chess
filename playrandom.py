import random
import position

class AIRandom:
    def __init__(self, white):
        self.white = white
        self.moves = position.Moves()
        self.name = 'AIRandom'

    def choose_move(self, gs):
        return random.choice(self.moves.legal_moves(gs.state))

    def game_over(self, game):
        pass
