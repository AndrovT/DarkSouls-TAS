"""
Basic Button presses and movements.

Core building blocks for more complicated scripts.
"""

__all__ = [
    'wait',
    'start',
    'select',
    'up',
    'down',
    'left',
    'right',
    'a',
    'b',
    'x',
    'y',
    'l1',
    'l2',
    'l3',
    'r1',
    'r2',
    'r3',
    'run',
    'walk',
    'run_back',
    'walk_back',
    'waitfor',
    'runfor',
    'walkfor',
]

from ..ds_tas import KeyPress

_runspeed = 32767
_walkspeed = 26500


# Wait
wait = KeyPress()

# Single Keypresses
start = KeyPress(start=1)
select = KeyPress(back=1)
up = KeyPress(dpad_up=1)
down = KeyPress(dpad_down=1)
left = KeyPress(dpad_left=1)
right = KeyPress(dpad_right=1)
a = KeyPress(a=1)
b = KeyPress(b=1)
x = KeyPress(x=1)
y = KeyPress(y=1)
l1 = KeyPress(l1=1)
l2 = KeyPress(l2=255)
l3 = KeyPress(l_thumb=1)
r1 = KeyPress(r1=1)
r2 = KeyPress(r2=255)
r3 = KeyPress(r_thumb=1)

# Joystick presses
run = KeyPress(l_thumb_y=_runspeed)
walk = KeyPress(l_thumb_y=_walkspeed)
run_back = KeyPress(l_thumb_y=-_runspeed)
walk_back = KeyPress(l_thumb_y=-_walkspeed)


def waitfor(frames):
    return KeyPress(frames=frames)


def runfor(frames):
    return KeyPress(frames=frames, l_thumb_y=_runspeed)


def walkfor(frames):
    return KeyPress(frames=frames, l_thumb_y=_walkspeed)
