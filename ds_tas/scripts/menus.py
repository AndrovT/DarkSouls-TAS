"""
Rapid Menuing sequences
"""

from ..ds_tas import KeySequence
from .basics import *

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
