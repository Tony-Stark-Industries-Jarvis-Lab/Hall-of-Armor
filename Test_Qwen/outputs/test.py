
import random

def get_user_choice():
    user_choice = input("Entrez votre choix (papier, ciseau, échecs): ").lower()
    while user_choice not in ['papier', 'ciseau', 'échecs']:
        print("Choix invalide. Veuillez entrer papier, ciseau, ou échecs.")
        user_choice = input("Entrez votre choix (papier, ciseau, échecs): ").lower()
    return user_choice

def get_computer_choice():
    return random.choice(['papier', 'ciseau', 'échecs'])

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Égalité"
    elif (user_choice == 'papier' and computer_choice == 'ciseau') or \
         (user_choice == 'ciseau' and computer_choice == 'échecs') or \
         (user_choice == 'échecs' and computer_choice == 'papier'):
        return "Vous avez gagné!"
    else:
        return "Vous avez perdu!"

def play_game():
    print("Bienvenue au jeu du papier, ciseau, échecs!")
    user_choice = get_user_choice()
    computer_choice = get_computer_choice()
    print(f"Vous avez choisi {user_choice}. L'ordinateur a choisi {computer_choice}.")
    result = determine_winner(user_choice, computer_choice)
    print(result)

if __name__ == "__main__":
    play_game()