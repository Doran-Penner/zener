import core
import time
from collections.abc import Callable
from core import MoveResult, Color, Move, Piece, Shape

type MoveGetter = Callable[
    [
        Color,
        dict[Color, dict[Shape, Piece]],
        list[Move],
        bool,
        Piece | None,
        Piece | None,
    ],
    Move,
]


def play_game(
    get_white_move: MoveGetter,
    get_black_move: MoveGetter,
    verbose: bool = False,
    sleep_time: float | None = None,
    draw_over: bool = True,
    end_of_turn_hook: Callable[[], None] | None = None,
) -> Color:
    def vp(*args, **kwargs):
        if verbose:
            print(args, kwargs)

    game = core.State()

    response, extra_info = ("filler", "")

    while response not in [
        MoveResult.WIN_WHITE,
        MoveResult.WIN_BLACK,
        MoveResult.ALREADY_OVER,
    ]:
        # Draw the board state
        if sleep_time is not None:
            time.sleep(sleep_time)
        if draw_over:
            print("\033[2J\033[H", end='')  # clear screen, return to terminal position 0,0
        game.draw_board()

        # Get the board state
        board = game.get_full_board()
        valid = game.get_valid_moves()
        player, responding, prev = game.get_next_move_new()
        _, required_move = game.get_next_move()

        # Ask the player for their move
        if player == Color.WHITE:
            move = get_white_move(player, board, valid, responding, prev, required_move)
        else:
            move = get_black_move(player, board, valid, responding, prev, required_move)

        # Apply it to the game
        response, extra_info = game.try_move(move)
        vp(f"{response}: {extra_info}")

        if end_of_turn_hook is not None:
            end_of_turn_hook()

    return game.get_who_won()
