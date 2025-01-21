#!/usr/bin/env python3

import sys
import subprocess
import json
import time
from play_game import play_game, MoveGetter
from core import Color, Move, Shape, State

def get_getter_for_player(player: Color) -> MoveGetter:
    def f(board, valid, responding, prev, next) -> Move:
        def get_board_json(board_state: dict[Color, dict[Shape, Piece]]):
            # do a bunch of dict mapping to convert the internal Piece
            # representations into normal json that other programs can read
            return {
                color: {
                    shape: {
                        "x": piece_obj.x,
                        "y": piece_obj.y,
                        "height": piece_obj.height,
                    }
                    for (shape, piece_obj) in colored_pieces.items()
                }
                for (color, colored_pieces) in board_state.items()
            }

        board = get_board_json(board)

        def get_moves_json(valid_moves: list[Move]):
            # quickndirty wrapper of above func for new json-oriented api
            lst = valid_moves
            ret = {shape: [] for shape in Shape}
            for move in lst:
                ret[move.shape].append({"x": move.x, "y": move.y})
            return ret

        valid = get_moves_json(valid)

        # run the relevant process
        combined_input = {
            "board": board,
            "player": player,
            "valid": valid,
            "responding": responding,
            "prev": prev,
        }
        bot_ret = subprocess.run(
            [sys.argv[1 if player == Color.WHITE else 2]],
            input=json.dumps(combined_input).encode(),
            capture_output=True,
        )

        # parse the bot's response
        bot_ret_json = json.loads(bot_ret.stdout.decode())
        print(f"Move attempt: {bot_ret_json}")
        if bot_ret.stderr != b"":
            print("Bot stderr:")
            print(bot_ret.stderr)
        # expect bot_ret's response to be
        # {"shape": "wave", "x": 2, "y": 1}
        return Move(
            player,
            Shape(bot_ret_json["shape"]),
            bot_ret_json["x"],
            bot_ret_json["y"],
        )

    return f


winner = play_game(
    get_white_move=get_getter_for_player(Color.WHITE),
    get_black_move=get_getter_for_player(Color.BLACK),
    verbose=True,
    sleep_time=0.25,
    draw_over=True,
)

print(f"Game is over! Winner: {winner}")
