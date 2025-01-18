#!/usr/bin/env python3

import sys
import subprocess
import json
import core

# very simple cli parsing
bots = {"white": sys.argv[1], "black": sys.argv[2]}

game = core.State()

response, extra_info = ("filler", "")

while response not in ["win_white", "win_black", "already_over"]:
    board = game.get_board_json()

    player, responding, prev = game.get_next_move_new()  # TODO make it

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
    sys.stdout.write(f"Move attempt: {bot_ret_json}\n")
    # TODO parse the above into a tuple that the engine wants
    engine_request = bot_ret_json

    response, extra_info = game.try_move(engine_request)
    sys.stdout.write(f"Engine response: {response}, {extra_info}\n")

sys.stdout.write(f"Game is over! Winner:\n{game.get_who_won()}\n")
