#!/usr/bin/env python3

import sys
import subprocess
import json
import time
from core import Color, Move, MoveResult, Shape, State

# very simple cli parsing
bots = {Color.WHITE: sys.argv[1], Color.BLACK: sys.argv[2]}

game = State()

response, extra_info = ("filler", "")

while response not in [
    MoveResult.WIN_WHITE,
    MoveResult.WIN_BLACK,
    MoveResult.ALREADY_OVER,
]:
    time.sleep(0.25)
    game.update_board()
    print("\033[2J\033[H")  # clear screen, return to terminal position 0,0
    game.draw_board()
    board = game.get_board_json()

    player, responding, prev = game.get_next_move_new()

    valid = game.get_moves_json()

    # run the relevant process
    combined_input = {
        "board": board,
        "player": player,
        "valid": valid,
        "responding": responding,
        "prev": prev,
    }
    bot_ret = subprocess.run(
        [bots[player]], input=json.dumps(combined_input).encode(), capture_output=True
    )

    # parse the bot's response
    bot_ret_json = json.loads(bot_ret.stdout.decode())
    print(f"Move attempt: {bot_ret_json}")
    if bot_ret.stderr != b"":
        print("Bot stderr:")
        print(bot_ret.stderr)
    # expect bot_ret's response to be
    # {"shape": "wave", "x": 2, "y": 1}
    engine_request = Move(
        player,
        Shape(bot_ret_json["shape"]),
        bot_ret_json["x"],
        bot_ret_json["y"],
    )

    response, extra_info = game.try_move(engine_request)
    sys.stdout.write(f"Engine response: {response}, {extra_info}\n")

sys.stdout.write(f"Game is over! Winner:\n{game.get_who_won()}\n")
