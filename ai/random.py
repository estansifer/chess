import random
import searchmoves

class AIRandom:
    def __init__(self, white):
        self.white = white
        self.name = 'AIRandom'

    def choose_move(self, gs):
        return random.choice(searchmoves.legal_moves(gs.state))

    def game_over(self, game):
        pass
