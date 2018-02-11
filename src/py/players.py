import human.playhuman
import ai.random
import ai.minmax

class Player:
    def __init__(self, name, factory):
        self.name = name
        self.factory = factory

random      = Player('AIRandom', ai.random.AIRandom)
human       = Player('Human', human.playhuman.Human)
minmax      = Player('AIMinMax', ai.minmax.ai_minmax)
minmaxq     = Player('AIMinMaxQ', ai.minmax.ai_minmax_quiescent)

players = [human, random, minmax, minmaxq]

def normalize_name(name):
    name = name.lower()
    if name[:2] == 'ai':
        return name[2:]
    else:
        return name

def lookup_player_by_name(name):
    for player in players:
        if normalize_name(player.name) == normalize_name(name):
            return player
    return None
