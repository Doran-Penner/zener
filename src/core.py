from copy import deepcopy
from functools import reduce
from itertools import chain
from enum import StrEnum, auto
from typing import Self


WIDTH = 5
HEIGHT = 7
RESET_ANSI_CODE = "\033[0m"


class Shape(StrEnum):
    CIRCLE = auto()
    PLUS = auto()
    WAVE = auto()
    SQUARE = auto()
    STAR = auto()

    @property
    def icon(self):
        match self:
            case Shape.CIRCLE:
                return "o"
            case Shape.PLUS:
                return "+"
            case Shape.WAVE:
                return "~"
            case Shape.SQUARE:
                return "▣"
            case Shape.STAR:
                return "*"


class Color(StrEnum):
    WHITE = auto()
    BLACK = auto()

    def other(self) -> Self:
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    @property
    def ansi(self) -> str:
        return f"\033[0;{31 if self == Color.WHITE else 34}m"


class MoveResult(StrEnum):
    MOVE_FAILURE = "move_failure"
    MOVE_SUCCESS = "move_success"
    WIN_WHITE = "win_white"
    WIN_BLACK = "win_black"
    ALREADY_OVER = "already_over"

    @classmethod
    def win_for_player(cls, player: Color) -> Self:
        return cls(f"win_{player.value}")


class Move:
    def __init__(self, player: Color, shape: Shape, x: int, y: int):
        self.player = player
        self.shape = shape
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (
            isinstance(other, Move)
            and self.player == other.player
            and self.shape == other.shape
            and self.x == other.x
            and self.y == other.y
        )

    def __repr__(self):
        return f"<moving the {self.player.value} {self.shape.value} to ({self.x}, {self.y})>"


class Piece:
    def __init__(self, shape: Shape, x_pos: int, y_pos: int, height: int, color: Color):
        self.x = x_pos
        self.y = y_pos
        self.shape = shape
        # note: height starts at 1, because it's easier to
        # think of an empty square as having height 0
        self.height = height

        self.color = color

    def __repr__(self):
        return f"<{self.color.value} {self.shape.value} at ({self.x}, {self.y}) with height {self.height}>"

    @property
    def icon(self):
        return self.shape.icon


class State:
    def __init__(self):
        # initialize to starting board
        white_pieces = {
            shape: Piece(shape, i, 0, 1, Color.WHITE) for (i, shape) in enumerate(Shape)
        }
        black_pieces = {
            shape: Piece(shape, (WIDTH - 1) - i, HEIGHT - 1, 1, Color.BLACK)
            for (i, shape) in enumerate(Shape)
        }
        self.state = {Color.WHITE: white_pieces, Color.BLACK: black_pieces}
        # specifies next valid move; first element is who goes next,
        # second is what piece they need to move as a string (or None)
        self.next_move = (Color.WHITE, None)
        self.prev_piece = None  # so we can't double-move
        self.winner = None
        # not currently used but it's nice to have when needed
        self.logged_moves = []

    def get_next_move_new(self) -> tuple[Color, bool, Piece | None]:
        player, req_piece = self.next_move
        if req_piece is None:
            responding = False
            prev = req_piece
        else:
            responding = True
            prev = self.prev_piece
        return player, responding, prev

    def draw_board(self) -> None:
        all_pieces = list(self.state[Color.WHITE].values()) + list(
            self.state[Color.BLACK].values()
        )
        print("╔═══════════════════╗")
        print("║                   ║")
        print("╠═══╤═══╤═══╤═══╤═══╣")
        # marginally faster than reversed(range(WIDTH)) even though Range.__reversed__ is special-cased in C
        # plus we want to stop early
        for y in range(HEIGHT - 1, 0, -1):
            row = ["  " for _ in range(5)]
            for x in range(WIDTH):
                pieces_at_pos = list(
                    filter(lambda piece: piece.x == x and piece.y == y, all_pieces)
                )
                if len(pieces_at_pos) == 0:
                    continue
                highest_piece = max(pieces_at_pos, key=lambda piece: piece.height)
                row[x] = (
                    highest_piece.color.ansi
                    + highest_piece.icon
                    + RESET_ANSI_CODE
                    + (
                        f"\\u208{highest_piece.height}".encode().decode(
                            "unicode-escape"
                        )
                        if highest_piece.height > 1
                        else " "
                    )
                )
            print("║ " + "│ ".join(row) + "║")
            print("╟───┼───┼───┼───┼───╢")
        y = 0
        row = ["  " for _ in range(5)]
        for x in range(WIDTH):
            pieces_at_pos = list(
                filter(lambda piece: piece.x == x and piece.y == y, all_pieces)
            )
            if len(pieces_at_pos) == 0:
                continue
            highest_piece = max(pieces_at_pos, key=lambda piece: piece.height)
            row[x] = (
                highest_piece.color.ansi
                + highest_piece.icon
                + RESET_ANSI_CODE
                + (
                    f"\\u208{highest_piece.height}".encode().decode("unicode-escape")
                    if highest_piece.height > 1
                    else " "
                )
            )
        print("║ " + "│ ".join(row) + "║")
        print("╠═══╧═══╧═══╧═══╧═══╣")
        print("║                   ║")
        print("╚═══════════════════╝")

    def get_who_won(self) -> Color | None:
        return self.winner

    def get_next_move(self) -> tuple[Color, Piece | None]:
        return self.next_move

    def get_full_board(self) -> dict[Color, dict[Shape, Piece]]:
        return deepcopy(self.state)  # copy so they can't modify it

    def get_valid_moves(self) -> list[Move]:
        # return list of valid moves, taking into account self.next_move
        player, piece_to_move = self.next_move
        colored_pieces = self.state[player]

        # do a flat map over everything we're allowed to move
        if piece_to_move is not None:
            pieces = [colored_pieces[piece_to_move]]
        else:
            pieces = colored_pieces.values()

        ret = []
        for moving_piece in pieces:
            # make sure we can't double-move
            if moving_piece.shape == self.prev_piece and piece_to_move is None:
                continue
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
            x_range = range(5)
            # have to only let players move off the board on the other side
            range_offset = 0 if player == Color.WHITE else -1
            y_range = range(0 + range_offset, 8 + range_offset)
            # we do this cursed thing because we want to filter AFTER mapping,
            # which normal python comprehensions don't do
            legal_moves = (
                Move(player, moving_piece.shape, final_x, final_y)
                for (dir_x, dir_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if (final_x := moving_piece.x + dir_x) in x_range
                and (final_y := moving_piece.y + dir_y) in y_range
            )
            ret.extend(legal_moves)
        return ret

    def get_player_cant_move(self) -> Color | None:
        # horrendous and cursed, avert ye eyes
        for player in Color:
            old_next = self.next_move
            old_prev = self.prev_piece
            self.next_move = (player, None)
            self.prev_piece = None
            if self.get_valid_moves() == []:
                return player
            self.next_move = old_next
            self.prev_piece = old_prev
        return None

    def _try_move(self, move: Move) -> tuple[MoveResult, str]:
        if self.winner is not None:
            return (
                MoveResult.ALREADY_OVER,
                f"Game has already finished! Team {self.winner} won",
            )

        if move not in self.get_valid_moves():
            return (MoveResult.MOVE_FAILURE, "not a valid move!")

        player = move.player
        shape = move.shape
        x = move.x
        y = move.y
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
                MoveResult.win_for_player(self.winner),
                f"team {self.winner} has won by moving a piece off the board!",
            )

        # increment move tracker
        self.prev_piece = shape
        if self.next_move[1] is None:
            # we just played free, now they respond
            self.next_move = (player.other(), shape)
        else:
            # now we get our free move
            self.next_move = (self.next_move[0], None)

        # check if someone loses by not moving
        if (loser := self.get_player_cant_move()) is not None:
            self.winner = loser.other()
            return (
                MoveResult.win_for_player(self.winner),
                f"Team {self.winner} has won by blocking the other team from moving!",
            )

        # continue until someone can move
        while self.get_valid_moves() == []:
            if self.next_move[1] is not None:
                print(f"LOG: skipping response move of {self.next_move[0]}")
                self.next_move = (self.next_move[0], None)
            else:
                print(f"LOG: skipping free move (and response) of {self.next_move[0]}")
                self.next_move = (self.next_move[0].other(), None)

        # if nothing else triggers, we return boring success
        return (MoveResult.MOVE_SUCCESS, "")

    # simple logging wrapper
    def try_move(self, move: Move) -> tuple[MoveResult, str]:
        out = self._try_move(move)
        self.logged_moves.append((move, out))
        return out
