"""
Here are examples, how the tas tools can be used.
Note that the first input after loading a savefile will not be registered.
"""

from .ds_tas import KeyPress, KeySequence

RUN = 32767
WALK = 26500


def get_quitout():
    return KeySequence(
        KeyPress(start=1),
        KeyPress(5),
        KeyPress(dpad_left=1),
        KeyPress(a=1),
        KeyPress(),
        KeyPress(dpad_up=1),
        KeyPress(a=1),
        KeyPress(),
        KeyPress(dpad_left=1),
        KeyPress(a=1),
    )


def get_moveswap(run_time=1, swap_up=False, wait_time=10):
    return KeySequence(
        KeyPress(run_time, l_thumb_y=RUN),
        KeyPress(l_thumb_y=RUN, b=1),
        KeyPress(wait_time),
        KeyPress(l1=1),
        KeyPress(start=1),
        KeyPress(5),
        KeyPress(dpad_right=1),
        KeyPress(a=1),
        KeyPress(),
        KeyPress(dpad_down=1),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(dpad_up=1 if swap_up else 0, dpad_down=0 if swap_up else 1),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(start=1),
        KeyPress(2),
        KeyPress(start=1),
    )


def get_itemswap(walk, toggle, use):
    return KeySequence(
        KeyPress(walk, l_thumb_y=WALK),
        KeyPress(x=1),
        KeyPress(),
        KeyPress(dpad_down=1),
        KeyPress(toggle, l_thumb_y=RUN),
        KeyPress(dpad_right=1, l_thumb_y=RUN),
        KeyPress(use, l_thumb_y=RUN),
        KeyPress(x=1),
    )


quitout = get_quitout()
moveswap_down = get_moveswap(swap_up=False)
moveswap_up = get_moveswap(swap_up=True)
