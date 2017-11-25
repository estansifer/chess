import sys
import os.path
import position
import searchmoves
import logger

class GameState:
    def __init__(self):
        self.state = position.initial_state()
        self.last_move = None
        self.turn = 1 # odd means white is about to play
        self.last_capture = 0
        self.history = [self.state]

    def copy(self):
        c = GameState()
        c.state = self.state
        c.last_move = self.last_move
        c.turn = self.turn
        c.last_capture = self.last_capture
        c.history = list(self.history)
        return c

    def apply(self, move):
        self.last_move = move
        new = move.apply(self.state)
        self.state = new
        if (move.piece is position.pawn) or move.capture:
            self.last_capture = self.turn
        self.turn += 1
        self.history.append(new)

    def draw3move(self):
        count = 0
        mask = position.bits_repitition_mask
        for old in self.history:
            if (old & mask) == (self.state & mask):
                count += 1
        return count >= 3

    def draw50move(self):
        return self.turn > self.last_capture + 100

class Game:
    def __init__(self, logging = True):
        self.gs = GameState()
        self.over = False
        self.draw = False
        self.winner = None
        self.players = {True : None, False : None}
        self.logging = logging
        self.logger = logger.Logger()

    def set_players(self, white, black):
        self.players = {True : white, False : black}
        self.logger.log_players(self.players)

    def play(self):
        while not self.over:
            white = ((self.gs.turn % 2) == 1)
            move = self.players[white].choose_move(self.gs.copy())

            self.gs.apply(move)
            self.logger.log_move(self.gs.copy())

            if move.is_resignation:
                self.over = True
                self.winner = not white
                break

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

        if self.logging:
            self.logger.save()
