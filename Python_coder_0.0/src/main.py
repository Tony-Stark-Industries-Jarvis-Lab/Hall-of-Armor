
# Import necessary libraries
import random

# Define constants for the game
ROCK = "rock"
PAPER = "paper"
SCISSORS = "scissors"
MAX_ATTEMPTS = 3

# Function to determine the winner
def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "It's a tie!"
    elif (player_choice == ROCK and computer_choice == SCISSORS) or \
         (player_choice == PAPER and computer_choice == ROCK) or \
         (player_choice == SCISSORS and computer_choice == PAPER):
        return "You win!"
    else:
        return "Computer wins!"

# Function to play the game
def play_game():
    player_score = 0
    computer_score = 0
    attempts = 0

    print("Welcome to Rock, Paper, Scissors!")
    print(f"You have {MAX_ATTEMPTS} attempts to win.")

    while attempts < MAX_ATTEMPTS:
        player_choice = input("Enter your choice (rock, paper, scissors): ").lower()

        if player_choice not in [ROCK, PAPER, SCISSORS]:
            print("Invalid choice. Please enter rock, paper, or scissors.")
            continue

        computer_choice = random.choice([ROCK, PAPER, SCISSORS])

        print(f"Computer chose {computer_choice}")

        result = determine_winner(player_choice, computer_choice)
        print(result)

        if result == "You win!":
            player_score += 1
        elif result == "Computer wins!":
            computer_score += 1

        attempts += 1

    print(f"\nGame Over!")
    print(f"Your score: {player_score}")
    print(f"Computer's score: {computer_score}")

# Main function to run the game
def main():
    play_game()

if __name__ == "__main__":
    main()