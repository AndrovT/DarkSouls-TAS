"""
Rapid Menuing sequences

Defined at 30fps
"""

from ds_tas.basics import *
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