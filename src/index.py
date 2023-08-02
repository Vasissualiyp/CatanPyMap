from src.main import new_random_game, new_pseudo_random_game, new_spiral_game, draw_game
from src.main import Parameters 

# index.py - continued

def main_mapgenerator(monitor_info, params):
    print("Welcome to Catan Map Generator!")
    print("Select the type of game you want to generate:")
    print("1. Spiral Game")
    print("2. Pseudorandom Game")
    print("3. Completely Random Game")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        game = new_spiral_game(monitor_info, params)
    elif choice == "2":
        game = new_pseudo_random_game(monitor_info, params)
    elif choice == "3":
        game = new_random_game(monitor_info, params)
    else:
        print("Invalid choice. Exiting.")
        return

    print(f"Generated game: {game}")
    print(f"Game code: {game}")

    # Draw the game board and save it as an image
    draw_game(game, params)
    #img.save("catan_board.png")

if __name__ == "__main__":
    monitor_info = (4096, 2160, 1210, 680)
    parameters = Parameters(monitor_info)
    main_mapgenerator(monitor_info, parameters)

