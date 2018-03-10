import human.playhuman
import ai.random
import ai.minmax

class Player:
    def __init__(self, name, factory):
        self.name = name
        self.factory = factory

random      = Player('AIRandom', ai.random.AIRandom)
human       = Player('Human', human.playhuman.Human)
minmax3     = Player('AIMinMax_3', ai.minmax.ai_minmax(3))
minmax4     = Player('AIMinMax_4', ai.minmax.ai_minmax(4))
minmaxq46   = Player('AIMinMaxQ_4_6', ai.minmax.ai_minmax_quiescent(4, 6))
minmaxq48   = Player('AIMinMaxQ_4_8', ai.minmax.ai_minmax_quiescent(4, 8))
minmaxq38   = Player('AIMinMaxQ_3_8', ai.minmax.ai_minmax_quiescent(3, 8))

players = [human, random, minmax3, minmax4, minmaxq46, minmaxq48, minmaxq38]

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
