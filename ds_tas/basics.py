"""
Basic Button presses and movements.

Core building blocks for more complicated scripts.

Combine them into sequences using & and + or making lists and
calling KeySequence(thelist)
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
    'sprint',
    'run',
    'walk',
    'run_back',
    'walk_back',
    'waitfor',
    'sprintfor',
    'runfor',
    'walkfor',
    'turn_around',
]

from .controller import KeyPress

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

# Combined actions
sprint = run & b


def waitfor(frames):
    return frames * wait


def runfor(frames):
    return frames * run


def walkfor(frames):
    return frames * walk


def sprintfor(frames):
    return frames * sprint


# Useful Helper
turn_around = waitfor(10) & run_back
