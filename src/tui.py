from core import State
from pprint import pp

game = State()

response, extra_info = ("filler", "")

while response not in ["win_white", "win_black", "already_over"]:
    player_turn, required_move = game.get_next_move()
    if required_move is None:
        required_move = "any"
    else:
        required_move = "their " + required_move
    print(f"It is {player_turn}'s move, who must move {required_move} piece next.")
    print("The board state is:")
    pp(game.get_full_board())
    print("Valid moves are:")
    pp(game.get_valid_moves())
    break  # TODO: ask user for input
    print()

print("Game is over!")
print(f"Winner: {game.get_who_won()}")
