"""
Rapid Menuing sequences

Defined at 30fps
"""

from ..basics import *
from ..controller import KeySequence

quitout = KeySequence([
    start,
    5 * wait,
    left,
    a,
    wait,
    up,
    a,
    wait,
    left,
    a
])

joy = KeySequence([
    select,
    right,
    wait,
    right,
    wait,
    right,
    a,
])


def level_fast(vit, att, end, stre, dex, res, inte, fth):
    # Assume you start in the level up window with vit highlighted
    inc_lvl = right + wait
    seq = KeySequence()
    for stat in [vit, att, end, stre, dex, res, inte, fth]:
        seq += inc_lvl * (stat - 1) + right
        seq += down
    return seq
