from core import State
from pprint import pp

game = State()

response, extra_info = ("filler", "")

while response not in ["win_white", "win_black", "already_over"]:
    player_turn, required_move = game.get_next_move()
    if required_move is None:
        required_move = "any"
    else:
        required_move = "their " + required_move
    print(f"It is {player_turn}'s move, who must move {required_move} piece next.")

    print("The board state is:")
    pp(game.get_full_board())

    print("Valid moves are:")
    pp(game.get_valid_moves())

    print("Input your move request.")
    in_player = input('player ("black" or "white"): ')
    in_shape = input('shape (e.g. "wave"): ')
    in_x = input('x (e.g. 2): ')
    in_y = input('y (e.g. 1): ')

    full_request = (in_player, in_shape, int(in_x), int(in_y))
    print(f"Your move: {full_request}")
    response, extra_info = game.try_move(full_request)

    print()
    print(f"{response}: {extra_info}")
    end_input = input("[Press any key to continue]")
    # sneaky debug console
    if end_input == "debug":
        breakpoint()
    print()

print("Game is over!")
print(f"Winner: {game.get_who_won()}")
