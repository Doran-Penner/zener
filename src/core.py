from copy import deepcopy
from functools import reduce
from itertools import chain

"""
We store state by player, then piece, then position & other data.
The piece is an object, everything else is a dict.
Here's an example of our database schema:
{
    "white": {
        "circle": Piece("circle", 0, 0, 0),
        "plus": Piece("plus", 1, 0, 0),
        ...
    },
    "black": ...,
}
(0, 0) is the lower left corner from white's perspective;
x values should be in [0, 4] and y values should be in [0, 6] (unless winning).

To get information about the game, use `get_full_board` to get the positions
of every piece on the board (as specified above), and `get_valid_moves`
to get all valid next moves. The move schema for a move to position (x, y) is
(player, shape, x, y), just a tuple of all the necessary information.

The way to make moves is with the `try_move` operation. The input schema is the
same as the above move schema, so if a strategy always chooses from the list of
`get_valid_moves` then it will always give an valid move request.
This gives a response as (response, extra_info).
`response` will always be one of
["move_failure", "move_success", "win_white", "win_black", "already_over"];
`extra_info` will be any extra information for human consumption.
Note that the turn tracker will silently move onto a player's second move if they
cannot make their first move, and if a player is unable to move at all then the
game will end without asking for input from the losing player - it will just
send a victory response to the last caller and then lock up.

Once the game is over, the core will lock up and not accept any more `try_move`s
(though it will still give information with `get` methods). At any time after
game end the `get_who_won()` method wll return the winner of the game, either
"black" or "white" (and that information will also be given on the winning move).
"""

# TODO do we need `extra_info`? We could just remove it...
# also I think the "programmatic API" should give functions the output of
# `get_next_move`, get_full_board`, and `get_valid_moves`
# and expect a return in the move schema
# the only parts that the external world should interface with are
# the get_* and try_move methods (and init); everything else is "pls don't touch"
# NOTE could change all the "will be" language to "is" once it's all settled


SHAPES = ["circle", "plus", "wave", "square", "star"]
WIDTH = 5
HEIGHT = 7


class Piece:
    def __init__(self, shape, x_pos, y_pos, height):
        assert shape in SHAPES, f"Invalid shape name: {shape}"
        self.x = x_pos
        self.y = y_pos
        self.shape = shape  # TODO do we need this at all?
        # note: height starts at 1, because it's easier to
        # think of an empty square as having height 0
        self.height = height

    def __repr__(self):
        return f"<{self.shape} at ({self.x}, {self.y}) with height {self.height}>"


class State:
    def __init__(self):
        # initialize to starting board
        white_pieces = {
            shape: Piece(shape, i, 0, 1) for (i, shape) in enumerate(SHAPES)
        }
        black_pieces = {
            shape: Piece(shape, (WIDTH - 1) - i, HEIGHT - 1, 1)
            for (i, shape) in enumerate(SHAPES)
        }
        self.state = {"white": white_pieces, "black": black_pieces}
        # specifies next valid move; first element is who goes next,
        # second is what piece they need to move as a string (or None)
        self.next_move = ("white", None)
        self.winner = None
        # small convenience function
        self.other_team = lambda color: "black" if color == "white" else "white"
        # also for debugging, we keeep full history of moves (and attempts)
        self.logged_moves = []

    def get_who_won(self):
        return self.winner

    def get_next_move(self):
        return self.next_move

    def get_full_board(self):
        return deepcopy(self.state)  # copy so they can't modify it

    def get_valid_moves(self):
        # return list of valid moves, taking into account self.next_move
        player, piece_to_move = self.next_turn
        colored_pieces = self.state[player]

        # do a flat map over everything we're allowed to move
        if piece_to_move is not None:
            pieces = [colored_pieces[piece_to_move]]
        else:
            pieces = colored_pieces.values()

        ret = []
        for moving_piece in pieces:
            # find out if piece is under something
            all_pieces = chain.from_iterable(
                map(lambda y: y.values(), self.state.values())
            )
            under = False
            for p in all_pieces:  # note that this includes self
                if (p.x, p.y) == (
                    moving_piece.x,
                    moving_piece.y,
                ) and p.height > moving_piece.height:
                    under = True
                    break
            if under:
                continue

            # now we can move, so find all in-bounds moves and extend ret with them
            x_range = range(4)
            # have to only let players move off the board on the other side
            range_offset = 0 if player == "white" else -1
            y_range = range(0 + range_offset, 8 + range_offset)
            # we do this cursed thing because we want to filter AFTER mapping,
            # which normal python comprehensions don't do
            legal_moves = (
                (final_x, final_y)
                for (dir_x, dir_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if (final_x := moving_piece.x + dir_x) in x_range
                and (final_y := moving_piece.y + dir_y) in y_range
            )
            # another way to do the above operation
            # legal_moves = filter(
            #     lambda pair: pair[0] in x_range and pair[1] in y_range,
            #     map(
            #         lambda pair: (pair[0] + moving_piece.x, pair[1] + moving_piece.y),
            #         [(-1, 0), (1, 0), (0, -1), (0, 1)],
            #     ),
            # )
            ret.extend(legal_moves)
        return ret

    def _try_move(self, move):
        if self.winner is not None:
            return (
                "already_over",
                f"Game has already finished! Team {self.winner} won",
            )

        if move not in self.get_valid_moves():
            return ("move_failure", "not a valid move!")

        player, shape, x, y = move
        piece = self.state[player][shape]
        piece.x = x
        piece.y = y
        # add 1 to final height for each other piece that's in the new position
        # (including self because a piece being "unstacked" is treated as height 1)
        # mwahahahaha I love iterators
        piece.height = reduce(
            lambda acc, new: acc + 1 if (new.x, new.y) == (piece.x, piece.y) else acc,
            chain.from_iterable(map(lambda y: y.values(), self.state.values())),
            0,
        )

        if piece.y not in range(HEIGHT):
            # escaped board! we assume it's a valid escape (not backwards or
            # sideways) because we only allow valid moves to get this far
            self.winner = player
            return (
                f"win_{self.winner}",
                f"team {self.winner} has won by moving a piece off the board!",
            )

        # increment move tracker
        if self.next_move[1] is None:
            self.next_move = (self.other_team(player), shape)
        else:
            self.next_move = (self.next_move[0], None)
        # also if the player cannot move their first piece, just carry on to 2nd move
        if self.get_valid_moves() == [] and self.next_move[1] is not None:
            self.next_move = (self.next_move[0], None)

        # check if someone loses by not moving
        if self.get_valid_moves() == []:
            self.winner = self.other_team(self.next_move[0])
            return (
                f"win_{self.winner}",
                f"Team {self.winner} has won by blocking the other team from moving!",
            )

        # if nothing else triggers, we return boring success
        return ("move_success", "")

    # simple logging wrapper
    def try_move(self, move):
        out = self._try_move(move)
        self.logged_moves.append(move, out)
        return out
