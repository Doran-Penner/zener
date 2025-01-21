from core import Color, Move, Shape
from play_game import play_game, MoveGetter
from pprint import pp


def get_getter_for_player(player: Color) -> MoveGetter:
    def f(board, valid, responding, prev, required_move) -> Move:
        if required_move is None:
            required_move = "any"
        else:
            required_move = "their " + required_move
        print(f"It is {player}'s move, who must move {required_move} piece next.")

        print("Valid moves are:")
        pp(valid)

        print("Input your move request.")
        in_player = input('player ("black" or "white"): ')
        in_shape = input('shape (e.g. "wave"): ')
        in_x = input("x (e.g. 2): ")
        in_y = input("y (e.g. 1): ")

        try:
            full_request = Move(Color(in_player), Shape(in_shape), int(in_x), int(in_y))
        except ValueError:
            print('ERROR: Invalid input type (e.g. "wave" for x)')
        print(f"Your move: {full_request}")

        return full_request

    return f


def end_of_turn():
    end_input = input("[Press any key to continue]")
    # sneaky debug console
    if end_input == "debug":
        breakpoint()
    print()


winner = play_game(
    get_white_move=get_getter_for_player(Color.WHITE),
    get_black_move=get_getter_for_player(Color.BLACK),
    verbose=True,
    sleep_time=0.25,
    draw_over=True,
    end_of_turn_hook=end_of_turn,
)

print(f"Game is over! Winner: {winner}")
