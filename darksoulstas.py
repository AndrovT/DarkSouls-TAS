"""
Launch a Dark Souls TAS Console with helpful commands pre-loaded.

Uses the STDLIB 'code' module to launch the terminal.
"""
import sys

import code
import copy
import textwrap

# noinspection PyUnresolvedReferences
from ds_tas import KeySequence, KeyPress
# noinspection PyUnresolvedReferences
from ds_tas.basics import *
# noinspection PyUnresolvedReferences
from ds_tas.scripts.menus import quitout, joy, level_fast
# noinspection PyUnresolvedReferences
from ds_tas.scripts.glitches import moveswap, joy_moveswap, roll_moveswap, reset_moveswap, itemswap, framedupe

__version__ = '2.1.0a1'

# Variable names to skip
skip_vars = ['sys', 'code', 'copy', 'textwrap', 'raw_banner', 'banner', 'skip_vars']

raw_banner = f"""
    Welcome to Dark Souls TAS Tools v{__version__}.
    
    Please read the readme at https://github.com/DavidCEllis/DarkSouls-TAS/tree/refactoring for a usage guide.
    Type exit() to quit.
"""

banner = textwrap.dedent(raw_banner).strip()


def tas_console():
    # Change the terminal prompt

    base_locals = {
        key: value for key, value in globals().items()
        if not (key.startswith('__') or key in skip_vars)
    }

    new_locals = copy.copy(base_locals)
    new_locals['tas_vars'] = base_locals
    new_locals['exit'] = sys.exit

    sys.ps1 = 'TAS>>> '
    code.interact(banner=banner, local=new_locals)


if __name__ == '__main__':
    tas_console()
