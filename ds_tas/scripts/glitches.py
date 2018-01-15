"""
Glitches

Note that these are defined for a 30FPS framerate - these will not work at 60fps.
"""

from ds_tas.basics import *
from .menus import joy
from ..controller import KeyPress, KeySequence


def moveswap(swap_up=False, too_heavy=True, l1_delay=0):
    """
    Base commands for moveswap (to be executed mid animation)

    :param swap_up: Moveswap to the item above
    :param too_heavy: Is the weapon too heavy to use one handed
    :param l1_delay: frames to wait after pressing L1 before trying to menu
    :return: KeySequence for moveswap
    """
    seq = KeySequence([
        l1,
        wait * l1_delay,
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

    return seq


def roll_moveswap(swap_up=False, too_heavy=True, run_time=1):
    """
    Perform a roll and moveswap off the roll
    :param swap_up: Moveswap to the item above
    :param too_heavy: Is the weapon too heavy to 1 hand
    :param run_time: Frames to run before moveswap
    :return: KeySequence for rolling moveswap
    """
    return KeySequence([
        run_time * run,
        run & b,
        10 * wait,
        moveswap(swap_up, too_heavy)
    ])


def reset_moveswap(swapped_up=False):
    """
    Reset from moveswapped state back to pre-moveswap state.

    :param swapped_up: Was the weapon that was moveswapped above the bow
    :return: KeySequence to revert moveswap
    """
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


def itemswap(walk_time, toggle, use):
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


joy_moveswap = joy + waitfor(100) + moveswap()
