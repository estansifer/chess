import playhuman
import ai.random
import ai.minmax

random = ai.random.AIRandom
human = playhuman.Human
minmax = ai.minmax.ai_minmax
minmaxq = ai.minmax.ai_minmax_quiescent

players = [human, random, minmax, minmaxq]

def lookup_player_by_name(name):
    name = name.lower()
    letters = []
    for letter in name:
        if letter.isalpha():
            letters.append(letter)
    name = ''.join(letters)
    if name[:2] == 'ai':
        name = name[2:]

    if name == 'human':
        return human
    if name == 'random':
        return random
    if name == 'minmax':
        return minmax
    if name == 'minmaxq':
        return minmaxq
