import sys
import os.path
import position

logging_dir = os.path.join(os.path.dirname(sys.argv[0]), 'logs')

def new_log_file():
    i = 0
    while True:
        path = os.path.join(logging_dir, 'game{:05d}'.format(i))
        if not os.path.exists(path):
            return path
        i += 1

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
        mask = position.bits_repition_mask
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
        self.moves = position.Moves()
        self.logging = logging
        if logging:
            self.logout = open(new_log_file(), 'w')

    def set_players(self, white, black):
        self.players = {True : white, False : black}

    def log(self, msg):
        if self.logging:
            self.logout.write(str(msg))
            self.logout.flush()

    def lognames(self):
        self.log('{} - {}\n'.format(self.players[True].name, self.players[False].name))

    def logresult(self):
        if self.over:
            self.log('\n')
            if self.draw:
                self.log('1/2 - 1/2\n')
            if self.winner is True:
                self.log('1 - 0\n')
            if self.winner is False:
                self.log('0 - 1\n')

    def logmove(self, name):
        if self.gs.turn % 2 == 0:
            self.log('  ')
        else:
            self.log('\n{:3d}. '.format((self.gs.turn + 1) // 2))
        while len(name) < 14:
            name = ' ' + name
        self.log(name)

    def closelog(self):
        if self.logging:
            self.logout.close()

    def play(self):
        self.lognames()
        while not self.over:
            white = ((self.gs.turn % 2) == 1)
            move = self.players[white].choose_move(self.gs.copy())
            if move is None:
                self.logmove('Resign')
                self.over = True
                self.winner = not white
                break

            self.logmove(move.name)
            self.gs.apply(move)

            if self.gs.draw3move() or self.gs.draw50move():
                self.draw = True
                self.over = True
                break

            if len(self.moves.legal_moves(self.gs.state)) == 0:
                self.over = True
                if not self.moves.in_check(self.gs.state):
                    self.draw = True
                else:
                    self.winner = white

        self.players[False].game_over(self)
        self.players[True].game_over(self)
        self.logresult()
        self.closelog()
