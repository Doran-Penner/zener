#!/usr/bin/env python3

import sys
from move_getters import get_from_bot
from play_game import play_game
from core import Color

p1_white_wins = 0
p1_black_wins = 0
p2_white_wins = 0
p2_black_wins = 0

GAME_COUNT = 1000
if len(sys.argv) > 3:
    GAME_COUNT = int(sys.argv[3])

print(f"Running {GAME_COUNT} games where {sys.argv[1]} is white and {sys.argv[2]} is black")
for i in range(GAME_COUNT):
    winner = play_game(
        get_white_move=get_from_bot(sys.argv[1]),
        get_black_move=get_from_bot(sys.argv[2]),
        above_board_text=f"Game {i+1}/{GAME_COUNT} (white: {sys.argv[1]}; black: {sys.argv[2]})"
    )
    if winner == Color.WHITE:
        p1_white_wins += 1
    else:
        p2_black_wins += 1
print(f"Running {GAME_COUNT} games where {sys.argv[2]} is white and {sys.argv[1]} is black")
for i in range(GAME_COUNT):
    winner = play_game(
        get_white_move=get_from_bot(sys.argv[2]),
        get_black_move=get_from_bot(sys.argv[1]),
        above_board_text=f"Game {i+1}/{GAME_COUNT} (white: {sys.argv[2]}; black: {sys.argv[1]})"
    )
    if winner == Color.WHITE:
        p2_white_wins += 1
    else:
        p1_black_wins += 1

print("RESULTS:")
print(f"{sys.argv[1]} won {p1_white_wins} games as white ({p1_white_wins/GAME_COUNT:.0%}) and {p1_black_wins} as black ({p1_black_wins/GAME_COUNT:.0%})")
print(f"{sys.argv[2]} won {p2_white_wins} games as white ({p2_white_wins/GAME_COUNT:.0%}) and {p2_black_wins} as black ({p2_black_wins/GAME_COUNT:.0%})")
