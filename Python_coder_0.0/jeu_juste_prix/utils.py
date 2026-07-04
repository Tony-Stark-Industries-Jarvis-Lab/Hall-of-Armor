
import random

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

def juste_prix():
  numero_a_deviner = random.randint(1, 100)
  nombre_essais = 0
  
  print(GREEN + "Welcome to the 'Guess the Price' game!" + RESET)
  print("Guess a number between 1 and 100.")
  
  while True:
    try:  
      devine = int(input(YELLOW + "Your guess: " + RESET))
      nombre_essais += 1  
      if devine < numero_a_deviner:
        print(RED + "Higher!" + RESET)
      elif devine > numero_a_deviner:
        print(RED + "Lower!" + RESET)
      else:
        print(GREEN + f"Well done! You found the number in {nombre_essais} tries." + RESET)
        break
    except ValueError:          
      print(RED + "Please enter a valid number." + RESET)
