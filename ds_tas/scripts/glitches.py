"""
Glitches

Note that these are defined for a 30FPS framerate - these will not work at 60fps.
"""

from ds_tas.basics import *
from .menus import joy
from ..controller import KeyPress, KeySequence


def get_moveswap_base(swap_up=False, too_heavy=True):
    """
    Base commands for moveswap (to be executed mid animation)

    :param swap_up: Moveswap to the item above
    :param too_heavy: Is the weapon too heavy to use one handed
    :return: KeySequence for moveswap
    """
    return KeySequence([
        l1,
        start,
        5 * wait,
        right,
        a,
        wait,
        down,
        a,
        2 * wait,
        up if swap_up else down,
        a,
        2 * wait,
        start,
        2 * wait,
        start if too_heavy else wait,
    ])


def get_moveswap(run_time=1, swap_up=False, wait_time=10):
    return KeySequence([
        run_time * run,
        run & b,
        wait_time * wait,
        get_moveswap_base(swap_up)
    ])


def get_reset_moveswap(swapped_up=False):
    return KeySequence([
        KeyPress(start=1),
        KeyPress(5),
        KeyPress(dpad_right=1),
        KeyPress(a=1),
        KeyPress(),
        KeyPress(dpad_down=1),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(dpad_up=0 if swapped_up else 1, dpad_down=1 if swapped_up else 0),
        KeyPress(a=1),
        KeyPress(2),
        KeyPress(start=1),
    ])


def get_itemswap(walk_time, toggle, use):
    return KeySequence([
        walkfor(walk_time),
        x,
        wait,
        down,
        runfor(toggle),
        run & right,
        runfor(use),
        x,
    ])


def framedupe(dupes):
    onedupe = x + waitfor(57) + x
    extradupe = waitfor(48) + waitfor(57) + x
    if dupes == 1:
        return onedupe
    elif dupes > 1:
        return onedupe + (dupes - 1) * extradupe


moveswap_down = get_moveswap(swap_up=False)
moveswap_up = get_moveswap(swap_up=True)
reset_up = get_reset_moveswap(swapped_up=True)
reset_down = get_reset_moveswap(swapped_up=False)

joy_moveswap = joy + KeyPress(100) + get_moveswap_base()
