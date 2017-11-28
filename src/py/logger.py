import sys
import os.path
import json

logging_dir = os.path.join(os.path.dirname(sys.argv[0]), '..', '..', 'logs')

class Logger:
    def __init__(self):
        self.players = {
                'white' : 'None',
                'black' : 'None'
            }
        self.moves = []
        self.result = 'unfinished'
        self.notes = []

    def choose_path(self):
        i = 0
        while True:
            path = os.path.join(logging_dir, 'game{:05d}'.format(i))
            if not os.path.exists(path):
                self.path = path
                return
            i += 1

    def log_players(self, players):
        self.players = {
                'white' : players[True].name,
                'black' : players[False].name
            }

    # Given the GameState after the move was performed
    #   time -- time in seconds
    #   annotation -- list of strings
    def log_move(self, gs, time = None, annotation = None):
        move = {
                    'turn' : gs.turn - 1,
                    'move' : gs.last_move.name,
                    'state' : int(gs.state)
                }
        if not (time is None):
            move['time'] = time
        if not (annotation is None):
            move['annotation'] = annotation
        self.moves.append(move)

    def log_result(self, draw, winner):
        if draw:
            self.result = '1/2 - 1/2'
        if winner is True:
            self.result = '1 - 0'
        if winner is False:
            self.result = '0 - 1'

    def log_note(self, note):
        self.notes.append(note)

    def to_json(self):
        return {
                    'players' : self.players,
                    'moves' : self.moves,
                    'result' : self.result,
                    'notes' : self.notes
                }

    def save(self):
        self.choose_path()
        with open(self.path, 'w') as f:
            json.dump(self.to_json(), f, indent = ' ')
