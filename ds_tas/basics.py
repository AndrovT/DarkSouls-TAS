"""
Basic Button presses and movements.

Core building blocks for more complicated scripts.

Combine them into sequences using & and + or making lists and
calling KeySequence(thelist)

Available KeyPresses:
    wait, start, select, up, down, left, right,
    a, b, x, y, l1, l2, l3, r1, r2, r3,
    sprint, run, walk, run_back, walk_back,
    run_left, run_right, walk_left, walk_right,
    aim_up, aim_down, aim_left, aim_right,
    s_aim_up, s_aim_down, s_aim_left, s_aim_right

Available Functions:
    waitfor, sprintfor, walkfor, runfor
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
    'run_left',
    'run_right',
    'walk_left',
    'walk_right',
    'aim_up',
    'aim_down',
    'aim_left',
    'aim_right',
    's_aim_up',
    's_aim_down',
    's_aim_left',
    's_aim_right',
    'waitfor',
    'sprintfor',
    'runfor',
    'walkfor',
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

# Basic Movement
run = KeyPress(l_thumb_y=_runspeed)
walk = KeyPress(l_thumb_y=_walkspeed)
run_back = KeyPress(l_thumb_y=-_runspeed)
walk_back = KeyPress(l_thumb_y=-_walkspeed)

run_left = KeyPress(l_thumb_x=-_runspeed)
run_right = KeyPress(l_thumb_x=_runspeed)
walk_left = KeyPress(l_thumb_x=-_walkspeed)
walk_right = KeyPress(l_thumb_y=_walkspeed)

# Camera Movement - s_ prefix for 'slow'
aim_up = KeyPress(r_thumb_y=32767)
aim_down = KeyPress(r_thumb_y=-32768)
aim_left = KeyPress(r_thumb_x=-32768)
aim_right = KeyPress(r_thumb_x=32767)

s_aim_up = KeyPress(r_thumb_y=16384)
s_aim_down = KeyPress(r_thumb_y=-16384)
s_aim_left = KeyPress(r_thumb_x=-16384)
s_aim_right = KeyPress(r_thumb_x=16384)

# Combined actions
sprint = run & b


def waitfor(frames):
    """
    Wait for <frames> frames.

    :param frames: Number of frames to wait for
    :return: Wait frames KeyPress
    """
    return frames * wait


def runfor(frames):
    """
    Run for <frames> frames.

    :param frames: Number of frames to run for
    :return: Run frames keypress
    """
    return frames * run


def walkfor(frames):
    """
    Run for <frames> frames.

    :param frames: Number of frames to run for
    :return: Run frames keypress
    """
    return frames * walk


def sprintfor(frames):
    """
    Run for <frames> frames.

    :param frames: Number of frames to run for
    :return: Run frames keypress
    """
    return frames * sprint

