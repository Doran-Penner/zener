from move_getters import get_from_human
from play_game import play_game, MoveGetter


def end_of_turn():
    end_input = input("[Press any key to continue]")
    # sneaky debug console
    if end_input == "debug":
        breakpoint()
    print()


winner = play_game(
    get_white_move=get_from_human,
    get_black_move=get_from_human,
    verbose=True,
    sleep_time=0.25,
    draw_over=True,
    end_of_turn_hook=end_of_turn,
)

print(f"Game is over! Winner: {winner}")
