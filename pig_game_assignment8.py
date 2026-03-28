import random
import argparse
import sys
import time

# ---------------------------
# Die Class
# ---------------------------
class Die:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

# ---------------------------
# Player Classes
# ---------------------------
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def reset(self):
        self.score = 0

    def decide(self, turn_total):
        """Human decision"""
        return input(f"{self.name}, roll (r) or hold (h)? ").lower()


class ComputerPlayer(Player):
    """Implements strategy:
       hold at min(25, 100 - current score)
    """
    def decide(self, turn_total):
        limit = min(25, 100 - self.score)
        if turn_total >= limit:
            print(f"{self.name} decides to HOLD")
            return 'h'
        else:
            print(f"{self.name} decides to ROLL")
            return 'r'

# ---------------------------
# Factory Pattern
# ---------------------------
class PlayerFactory:
    @staticmethod
    def create_player(player_type, name):
        if player_type == "human":
            return Player(name)
        elif player_type == "computer":
            return ComputerPlayer(name)
        else:
            raise ValueError("Invalid player type")

# ---------------------------
# Game Class
# ---------------------------
class Game:
    def __init__(self, player1_type, player2_type):
        self.players = [
            PlayerFactory.create_player(player1_type, "Player 1"),
            PlayerFactory.create_player(player2_type, "Player 2")
        ]
        self.die = Die()
        self.target_score = 100

    def play(self):
        for p in self.players:
            p.reset()

        current_player_idx = 0
        game_over = False

        print("\n=== Let's Play Pig! ===")

        while not game_over:
            player = self.players[current_player_idx]
            turn_total = 0

            print(f"\n--- {player.name}'s Turn ---")

            while True:
                print(f"Total Score: {player.score} | Turn Total: {turn_total}")

                decision = player.decide(turn_total)

                if decision == 'r':
                    roll = self.die.roll()
                    print(f"-> Rolled a {roll}")

                    if roll == 1:
                        print("-> Pig! Turn over.")
                        turn_total = 0
                        break
                    else:
                        turn_total += roll

                elif decision == 'h':
                    print(f"-> Holding {turn_total}")
                    break

                else:
                    print("Invalid input.")

            player.score += turn_total
            print(f">>> {player.name} score: {player.score}")

            if player.score >= self.target_score:
                print(f"\n*** {player.name} WINS! ***")
                game_over = True
            else:
                current_player_idx = (current_player_idx + 1) % 2

# ---------------------------
# Proxy Pattern (Timed Game)
# ---------------------------
class TimedGameProxy:
    def __init__(self, game):
        self.game = game
        self.start_time = None
        self.time_limit = 60  # 60 seconds

    def play(self):
        self.start_time = time.time()

        for p in self.game.players:
            p.reset()

        current_player_idx = 0

        print("\n=== Timed Pig Game (1 minute) ===")

        while True:
            # Check time
            if time.time() - self.start_time >= self.time_limit:
                print("\n*** TIME IS UP! ***")
                self.declare_winner()
                return

            player = self.game.players[current_player_idx]
            turn_total = 0

            print(f"\n--- {player.name}'s Turn ---")

            while True:
                if time.time() - self.start_time >= self.time_limit:
                    print("\n*** TIME IS UP! ***")
                    self.declare_winner()
                    return

                print(f"Total Score: {player.score} | Turn Total: {turn_total}")

                decision = player.decide(turn_total)

                if decision == 'r':
                    roll = self.game.die.roll()
                    print(f"-> Rolled a {roll}")

                    if roll == 1:
                        turn_total = 0
                        break
                    else:
                        turn_total += roll

                elif decision == 'h':
                    break

            player.score += turn_total
            print(f">>> {player.name} score: {player.score}")

            if player.score >= self.game.target_score:
                print(f"\n*** {player.name} WINS! ***")
                return

            current_player_idx = (current_player_idx + 1) % 2

    def declare_winner(self):
        p1, p2 = self.game.players
        if p1.score > p2.score:
            print(f"{p1.name} wins with {p1.score} points!")
        elif p2.score > p1.score:
            print(f"{p2.name} wins with {p2.score} points!")
        else:
            print("It's a tie!")

# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Pig Game with Design Patterns")

    parser.add_argument('--player1', choices=['human', 'computer'], default='human')
    parser.add_argument('--player2', choices=['human', 'computer'], default='human')
    parser.add_argument('--timed', action='store_true')

    args = parser.parse_args()

    random.seed(0)

    base_game = Game(args.player1, args.player2)

    # Use Proxy if timed
    game = TimedGameProxy(base_game) if args.timed else base_game

    while True:
        game.play()

        again = input("\nPlay again? (y/n): ").lower()
        if again != 'y':
            print("Thanks for playing!")
            sys.exit()

if __name__ == "__main__":
    main()