# Zener (WIP)
Playable implementation of the board game
[Zener](https://en.boardgamearena.com/tutorial?game=zener&tutorial=817),
make for Paideia 2025.

## How to use

The code is all in the `src/` directory. The core gameplay, including move validation, checking who wins, and so on is stored in `core.py`. To actually play the game, run:
```
python3 src/api.py <PLAYER_WHITE> <PLAYER_BLACK>
```
where `PLAYER_X` is \[a path to] an executable that will "play the game" via stdio, described below. Alternatively, with `python3 src/tui.py` you can interactively play both sides of the game.

There are no dependencies (except for python3); you should just be able to clone this repository or copy the files directly and run it.

## Interface

The "player programs" should expect [JSON](https://en.wikipedia.org/wiki/JSON#Syntax) from _stdin_ as input and output JSON to _stdout_, specified below. If you're unfamiliar with these terms, they're ways for programs to communicate regardless of the programming language they're written in, and any language you use will have a way to interact with it easily. (Look below for an example in python.) You can also print to _stderr_ for logging messages that won't disturb the actual output of the program.

### Specification

The program will be given json via stdin and output json to stdout. Input will contain:
- `"board"`: the board state
- `"player"`: whose turn it is to move
- `"valid"`: valid moves for that player
- `"responding"`: whether this move is the player's 1st move, so they're _responding_ to the other player's move, or their 2nd "free move" when they can move (almost) any piece they want
- `"prev"`: the previous piece moved. If the above `responding` is false, it's the piece that this player moved for their 1st move and thus cannot move again; if `responding` is true, then it's the piece they must move next (for their 1st turn).
The output must be a json object containing the `shape` to move and the `x` and `y` values to move it to. See the example below for the exact structure of those elements.

<details>
<summary>Example: starting input and possible output</summary>
Here's the first input that a program will receive. The spacing has been added for readability, but will probably not be like this in the actual output; we strongly recommend you use a pre-existing json parsing library instead of writing your own.
```json
{
  "board": {
    "white": {
      "circle": { "x": 0, "y": 0, "height": 1 },
      "plus": { "x": 1, "y": 0, "height": 1 },
      "wave": { "x": 2, "y": 0, "height": 1 },
      "square": { "x": 3, "y": 0, "height": 1 },
      "star": { "x": 4, "y": 0, "height": 1 }
    },
    "black": {
      "circle": { "x": 4, "y": 6, "height": 1 },
      "plus": { "x": 3, "y": 6, "height": 1 },
      "wave": { "x": 2, "y": 6, "height": 1 },
      "square": { "x": 1, "y": 6, "height": 1 },
      "star": { "x": 0, "y": 6, "height": 1 }
    }
  },
  "player": "white",
  "valid": {
    "circle": [ { "x": 1, "y": 0 }, { "x": 0, "y": 1 } ],
    "plus": [ { "x": 0, "y": 0 }, { "x": 2, "y": 0 }, { "x": 1, "y": 1 } ],
    "wave": [ { "x": 1, "y": 0 }, { "x": 3, "y": 0 }, { "x": 2, "y": 1 } ],
    "square": [ { "x": 2, "y": 0 }, { "x": 4, "y": 0 }, { "x": 3, "y": 1 } ],
    "star": [ { "x": 3, "y": 0 }, { "x": 4, "y": 1 } ]
  },
  "responding": false,
  "prev": null
}
```
And here's a potential output:
```json
{
  "shape": "circle",
  "x": 0,
  "y": 1
}
```
</details>

### Example python code

Here's a basic program that chooses the first valid move. We use the built-in libraries `json` and `sys` to easily read and write json to stdin/out. Note the weird comment at the top: to make sure our api knows how to run (e.g. Python or Java or some other language), we need to specify the program that will run it. This is not necessary for compiled languages like C.
```py
#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)  # load the input data
valid = data['valid']
for piece in valid:
    # search for a valid move
    if len(valid[piece]) > 0:
        # "dump" aka write this dictionary to stdout
        json.dump({
            "shape": piece,
            "x": valid[piece][0]["x"],
            "y": valid[piece][0]["y"]
        }, sys.stdout)
        print("found it!", file=sys.stderr)  # optional: write whatever logs you want
        break  # make sure you don't keep writing output!
```

## Contributing

This is a small project and surely has bugs. Any/all contributions are welcome!
