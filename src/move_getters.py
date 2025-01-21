import json
import subprocess
from core import Color, Move, Piece, Shape
from play_game import MoveGetter
from pprint import pp


def get_from_human(
    player: Color,
    board: dict[Color, dict[Shape, Piece]],
    valid: list[Move],
    responding: bool,
    prev: Piece | None,
    required_move: Piece | None,
) -> Move:
    if required_move is None:
        required_move = "any"
    else:
        required_move = "their " + required_move
    print(f"It is {player}'s move, who must move {required_move} piece next.")

    print("Valid moves are:")
    pp(valid)

    move_ok = False
    while not move_ok:
        print("Input your move request.")
        in_shape = input('shape (e.g. "wave"): ')
        in_x = input("x (e.g. 2): ")
        in_y = input("y (e.g. 1): ")

        try:
            move = Move(player, Shape(in_shape), int(in_x), int(in_y))
        except ValueError:
            print('ERROR: Invalid input type (e.g. "wave" for x)')
            continue

        print(f"Your move: {move}")
        if move in valid:
            move_ok = True
        else:
            print("This is not a valid move!")

    return move


def get_from_bot(bot_path: str) -> MoveGetter:
    def f(
        player: Color,
        board: dict[Color, dict[Shape, Piece]],
        valid: list[Move],
        responding: bool,
        prev: Piece | None,
        next: Piece | None,
    ) -> Move:
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
            [bot_path],
            input=json.dumps(combined_input).encode(),
            capture_output=True,
        )

        if bot_ret.returncode != 0:
            print(f"WARN: {player.value}'s bot returned exit code {bot_ret.returncode}")
            print("This could indicate a problem with the bot.")
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
