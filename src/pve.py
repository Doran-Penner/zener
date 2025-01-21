import sys
from move_getters import get_from_human, get_from_bot
from play_game import play_game, MoveGetter


winner = play_game(
    get_white_move=get_from_human,
    get_black_move=get_from_bot(sys.argv[1]),
    verbose=True,
    sleep_time=0.25,
    draw_over=True,
)

print(f"Game is over! Winner: {winner}")