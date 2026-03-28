import random
import argparse
import sys
import time

# ---------------------------
# Die Class
# ---------------------------
class Die:
    """Represents a standard 6-sided die."""
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

# ---------------------------
# Player Classes (Inheritance)
# ---------------------------
class Player:
    """Base class representing a human player."""
    def __init__(self, name):
        self.name = name
        self.score = 0

    def reset(self):
        self.score = 0

    def decide(self, turn_total):
        """Asks the human player for their decision."""
        while True:
            choice = input(f"{self.name}, roll (r) or hold (h)? ").lower()
            if choice in ['r', 'h']:
                return choice
            print("Invalid input. Please enter 'r' or 'h'.")

class ComputerPlayer(Player):
    """Computer player that inherits from Player and implements a specific strategy."""
    def decide(self, turn_total):
        """
        Strategy: hold at the lesser of 25 and 100 - current score.
        Otherwise, roll.
        """
        limit = min(25, 100 - self.score)
        
        # Add a small delay so the computer's turns are readable in the console
        time.sleep(1) 

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
    """Instantiates the correct Player class based on the requested type."""
    @staticmethod
    def create_player(player_type, name):
        if player_type.lower() == "human":
            return Player(name)
        elif player_type.lower() == "computer":
            return ComputerPlayer(name)
        else:
            raise ValueError(f"Invalid player type: {player_type}")

# ---------------------------
# Core Game Class
# ---------------------------
class Game:
    """The standard game of Pig."""
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
        print("\n=== Let's Play Pig! ===")

        while True:
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
                        print("-> Pig! Turn over. You lose your turn points.")
                        turn_total = 0
                        break
                    else:
                        turn_total += roll
                elif decision == 'h':
                    print(f"-> Holding {turn_total} points.")
                    break

            player.score += turn_total
            print(f">>> {player.name}'s total score is now: {player.score}")

            if player.score >= self.target_score:
                print(f"\n*** {player.name} WINS! ***")
                return

            # Switch to the other player
            current_player_idx = (current_player_idx + 1) % 2

# ---------------------------
# Proxy Pattern
# ---------------------------
class TimedGameProxy:
    """Proxy for Game that enforces a 1-minute time limit without altering Game logic."""
    def __init__(self, game):
        self.game = game
        self.time_limit = 60 # 60 seconds (1 minute)

    def check_time(self, start_time):
        """Helper method to check if time is up."""
        if time.time() - start_time >= self.time_limit:
            print("\n*** TIME IS UP! (1 minute has elapsed) ***")
            self.declare_winner()
            return True
        return False

    def play(self):
        start_time = time.time()
        for p in self.game.players:
            p.reset()

        current_player_idx = 0
        print("\n=== Timed Pig Game (1 minute limit) ===")

        while True:
            # Check time before starting a new turn
            if self.check_time(start_time): return

            player = self.game.players[current_player_idx]
            turn_total = 0
            print(f"\n--- {player.name}'s Turn ---")

            while True:
                # Check time before every single decision step
                if self.check_time(start_time): return

                print(f"Total Score: {player.score} | Turn Total: {turn_total}")
                decision = player.decide(turn_total)

                if decision == 'r':
                    roll = self.game.die.roll()
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

            player.score += turn_total
            print(f">>> {player.name}'s total score is now: {player.score}")

            if player.score >= self.game.target_score:
                print(f"\n*** {player.name} WINS with {player.score} points! ***")
                return

            current_player_idx = (current_player_idx + 1) % 2

    def declare_winner(self):
        p1, p2 = self.game.players
        if p1.score > p2.score:
            print(f"{p1.name} wins with {p1.score} points vs {p2.score} points!")
        elif p2.score > p1.score:
            print(f"{p2.name} wins with {p2.score} points vs {p1.score} points!")
        else:
            print(f"It's a tie! Both players have {p1.score} points.")

# ---------------------------
# Main Execution
# ---------------------------
def main():
    # Setup Argument Parser
    parser = argparse.ArgumentParser(description="Play the game of Pig (with optional time limit).")
    parser.add_argument('--player1', choices=['human', 'computer'], default='human', help='Type of Player 1')
    parser.add_argument('--player2', choices=['human', 'computer'], default='human', help='Type of Player 2')
    parser.add_argument('--timed', action='store_true', help='Play a 1-minute timed version of the game')
    
    args = parser.parse_args()

    # Seed for predictability (optional, but good for testing)
    random.seed(0)

    # Initialize the base game using the Factory
    base_game = Game(args.player1, args.player2)
    
    # Wrap in Proxy if --timed argument is present
    game = TimedGameProxy(base_game) if args.timed else base_game

    # Game Loop
    while True:
        game.play()

        again = input("\nPlay again? (y/n): ").lower()
        if again != 'y':
            print("Thanks for playing!")
            sys.exit()

if __name__ == "__main__":
    main()
