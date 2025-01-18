How to use stdio and call other processes!!

```py
#!/usr/bin/env python3

import sys
import subprocess

# here we just spit it back out, but we can do so much more if we want to
for x in sys.stdin:
    sys.stdout.write(x)

ret = subprocess.run(["ls"], capture_output=True)
ret2 = subprocess.run(["sleep", "5"], capture_output=True)

print(ret.stdout)  # can also check ret.returncode
```

So for our API, the final executable should take two filename arguments
which are the "players," the first is the white player and the second is
the black.

***

todos at this late hour:
- change turn accounting to properly skip turns, end game, etc
- change how engine accounts for turns, move to our action-response model
  - this will maybe break `tui.py` but whatever
- make this info accessible via some `get_next_move_info()` funciton
  - make sure the names and such line up with how it's called in api.py
and then I think we're done?
