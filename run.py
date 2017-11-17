import game
import players

def run():
    g = game.Game()
    g.set_players(players.human(True), players.random(False))
    g.play()

if __name__ == "__main__":
    run()
