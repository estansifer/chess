import sys
import os.path
import position
import searchmoves
import logger
import timer

class GameState:
    def __init__(self):
        self.state = position.initial_state()
        self.states = [self.state]
        self.moves = []
        self.turn = len(self.states)

    def copy(self):
        c = GameState()
        c.state = self.state
        c.moves = list(self.moves)
        c.states = list(self.states)
        c.turn = self.turn
        return c

    def apply(self, move):
        self.state = move.apply(self.state)
        self.states.append(self.state)
        self.moves.append(move)
        self.turn += 1

    def rewind(self, steps = 2):
        self.turn = max(self.turn - steps, 1)
        self.states = self.states[:self.turn]
        self.moves = self.moves[:self.turn - 1]
        self.state = self.states[-1]

    def draw3move(self):
        count = 0
        mask = position.mask_repitition
        for old in self.states:
            if (old & mask) == (self.state & mask):
                count += 1
        return count >= 3

    # May have off-by-1 error, didn't bother checking
    def draw50move(self):
        if self.turn > 101:
            for move in self.moves[-100:]:
                if (move.piece is position.pawn) or move.capture:
                    return False
            return True
        return False

class Game:
    def __init__(self, logging = True):
        self.gs = GameState()
        self.over = False
        self.draw = False
        self.winner = None
        self.players = {True : None, False : None}
        self.timers = {True : timer.Timer(), False: timer.Timer()}
        self.logging = logging
        self.logger = logger.Logger()

    def set_players(self, white, black):
        self.players = {True : white, False : black}
        self.logger.log_players(self.players)

    def play(self):
        while not self.over:
            white = ((self.gs.turn % 2) == 1)
            gscopy = self.gs.copy()
            with self.timers[white]:
                move = self.players[white].choose_move(gscopy)

            if move.is_resignation:
                self.over = True
                self.winner = not white
                break

            if move.is_undo:
                self.gs.rewind(2)
            else:
                self.gs.apply(move)

            self.logger.log_move(self.gs.copy(), time = self.timers[white].last())

            if self.gs.draw3move() or self.gs.draw50move():
                self.over = True
                self.draw = True
                break

            if len(searchmoves.legal_moves(self.gs.state)) == 0:
                self.over = True
                if not searchmoves.in_check(self.gs.state):
                    self.draw = True
                else:
                    self.winner = white

        self.players[False].game_over(self)
        self.players[True].game_over(self)
        self.logger.log_result(self.draw, self.winner)
        self.logger.log_note('White time usage: {}'.format(self.timers[True].summary()))
        self.logger.log_note('Black time usage: {}'.format(self.timers[False].summary()))

        if self.logging:
            self.logger.save()
