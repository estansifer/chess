import playrandom
import playhuman

random = playrandom.AIRandom
human = playhuman.Human

players = [human, random]

def lookup_player_by_name(name):
    name = name.lower()
    if name == 'human':
        return human
    if name in ['random', 'airandom']:
        return random
