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


def level_fast(
        vitality=0,
        attunement=0,
        endurance=0,
        strength=0,
        dexterity=0,
        resistance=0,
        intelligence=0,
        faith=0
):
    """
    Level up as quickly as possible. Any unused parameters won't be levelled.

    :param vitality:
    :param attunement:
    :param endurance:
    :param strength:
    :param dexterity:
    :param resistance:
    :param intelligence:
    :param faith:
    :return: Keysequence for level up
    """
    # Assume you start in the level up window with vit highlighted
    inc_lvl = right + wait
    seq = KeySequence()
    stats = [
        vitality,
        attunement,
        endurance,
        strength,
        dexterity,
        resistance,
        intelligence,
        faith,
    ]
    for stat in stats:
        if stat > 0:
            seq += inc_lvl * (stat - 1) + right
        else:
            # if we don't level a stat we need to wait
            # a frame so the next down press registers.
            seq += wait
        seq += down
    return seq
