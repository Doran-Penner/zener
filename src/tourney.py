#!/usr/bin/env python3

import sys
from core import Color
from move_getters import get_from_bot
from play_game import play_game

PLAYERS = sys.argv[1:]
PLAYER_COUNT = len(PLAYERS)

print("You've passed the following bots as players:")
print(PLAYERS)

winners: dict[str, dict[str, Color]] = {bot: {} for bot in PLAYERS}
stats: dict[str, tuple[float, float, float]] = {}

for white_bot in PLAYERS:
    for black_bot in PLAYERS:
        if white_bot == black_bot:
            continue
        winner = play_game(get_from_bot(white_bot), get_from_bot(black_bot))
        print(f"white: {white_bot}; black: {black_bot}; winner: {winner}")
        winners[white_bot][black_bot] = winner


for bot in PLAYERS:
    white_wins = sum(
        1 if winners[bot][other] == Color.WHITE else 0 for other in winners[bot]
    )
    black_wins = sum(
        1 if winners[other][bot] == Color.BLACK else 0 for other in winners[bot]
    )
    white_win_rate = white_wins / (PLAYER_COUNT - 1)
    black_win_rate = black_wins / (PLAYER_COUNT - 1)
    win_rate = (white_wins + black_wins) / ((PLAYER_COUNT * 2) - 2)
    stats[bot] = (white_win_rate, black_win_rate, win_rate)

print("\033[2J\033[H")  # clear screen, return to terminal position 0,0
print("OVERALL:")
for bot in sorted(stats, key=lambda bot: stats[bot][2], reverse=True):
    print(f"- {stats[bot][2]:.0%} ({bot})")

print("WHEN GOING FIRST:")
for bot in sorted(stats, key=lambda bot: stats[bot][0], reverse=True):
    print(f"- {stats[bot][0]:.0%} ({bot})")

print("WHEN GOING SECOND:")
for bot in sorted(stats, key=lambda bot: stats[bot][1], reverse=True):
    print(f"- {stats[bot][1]:.0%} ({bot})")
