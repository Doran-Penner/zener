#!/usr/bin/env python3

import sys
import subprocess
import json
import core
import time

# very simple cli parsing
bots = {"white": sys.argv[1], "black": sys.argv[2]}

game = core.State()

response, extra_info = ("filler", "")

while response not in ["win_white", "win_black", "already_over"]:
    time.sleep(0.25)
    game.update_board()
    print("\033[2J\033[H") #clear screen, return to terminal position 0,0
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
    if bot_ret.stderr != b'':
        print("Bot stderr:")
        print(bot_ret.stderr)
    # expect bot_ret's response to be
    # {"shape": "wave", "x": 2, "y": 1}
    engine_request = (
        player,
        bot_ret_json["shape"],
        bot_ret_json["x"],
        bot_ret_json["y"],
    )

    response, extra_info = game.try_move(engine_request)
    sys.stdout.write(f"Engine response: {response}, {extra_info}\n")

sys.stdout.write(f"Game is over! Winner:\n{game.get_who_won()}\n")
