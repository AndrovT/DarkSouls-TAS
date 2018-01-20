"""
Launch a Dark Souls TAS Console with helpful commands pre-loaded.

Uses the STDLIB 'code' module to launch the terminal.
"""
import sys
import pydoc
import code
import textwrap

from ds_tas import KeySequence, KeyPress, basics
from ds_tas.scripts import menus, glitches

__version__ = '2.1.0b3'

# Variable names to skip
skip_vars = ['sys', 'code', 'copy', 'textwrap', 'raw_banner', 'banner', 'skip_vars']

raw_banner = f"""
    Welcome to Dark Souls TAS Tools v{__version__}.
    
    Basic Keypresses:
        wait, start, select, up, down, left, right,
        a, b, x, y, l1, l2, l3, r1, r2, r3, 
        sprint, run, walk, run_back, walk_back, 
        run_left, run_right, walk_left, walk_right,
        aim_up, aim_down, aim_left, aim_right,
        s_aim_up, s_aim_down, s_aim_left, s_aim_right
        
    Basic Functions:
        waitfor, walkfor, runfor, sprintfor
    
    Recording and Playback:
        Functions:
            record, playback, save, load
        Current Sequence:
            recording
    
    Raw Classes:
        KeyPress, KeySequence
    
    Extension modules:
        menus, glitches
        
    Chain KeyPresses and KeySequences using '+' and '*'. 
    Combine KeyPresses using '&'.
    
    eg: running_jump = (run & b) * 30 + run + (run & b) * 2
    
    When a KeyPress or KeySequence has been built up use .execute() to run it.
    
    Use help(nameofthing) to see the documentation and functions for that object. 
    (This will also give internal information)
    
    Please read the readme at 
    https://github.com/DavidCEllis/DarkSouls-TAS/tree/refactoring for examples.
    
    Type exit() to quit.
"""

banner = textwrap.dedent(raw_banner).strip()

# Define base_locals globally so recording works as intended
base_locals = {
    key: getattr(basics, key) for key in basics.__all__
}

base_locals['KeySequence'] = KeySequence
base_locals['KeyPress'] = KeyPress
base_locals['menus'] = menus
base_locals['glitches'] = glitches

base_locals['recording'] = basics.select + basics.right + basics.a


class Helper:
    """
    Helper class for interactive terminal.

    Gives basic information on using keypresses and keysequences or help documentation
    on functions and classes.

    This is a class so it could have a helpful repr.
    """
    def __call__(self, obj):
        if isinstance(obj, (KeySequence, KeyPress)):
            print(f"{obj}\nType '<name>.execute()' to perform this action in game.")
        else:
            pydoc.help(obj)

    def __repr__(self):
        return "Help Method - use help(item) to get information on the item."


def record(start_delay=5, record_time=None, button_wait=True):
    """
    Record the input and store a global KeySequence.

    Press start and select at the same time to stop the recording.

    :param start_delay: Time before recording will start (in seconds)
    :param record_time: Length of time to record for (in seconds), None will record indefinitely.
    :param button_wait: Wait for a button input before starting recording
    """
    global base_locals
    base_locals['recording'] = KeySequence.record(start_delay, record_time, button_wait)
    print('Recording stored as `recording`')


def playback(start_delay=None, igt_wait=False):
    """
    Playback the current recording.

    :param start_delay: Time before playback commences
    :param igt_wait: wait for IGT to change before playback commenses
    """
    global base_locals
    base_locals['recording'].execute(start_delay, igt_wait)


def save(filename):
    """
    Save the current recording to the path given.

    :param filename: Recording output path
    """
    global base_locals
    base_locals['recording'].to_file(filename)


def load(filename):
    """
    Reload a recording from a given path.

    :param filename: path of the keysequence to load.
    """
    global base_locals
    base_locals['recording'] = KeySequence.from_file(filename)


def tas_console():
    # Get the basic key commands for the command prompt

    base_locals['record'] = record
    base_locals['playback'] = playback
    base_locals['save'] = save
    base_locals['load'] = load

    base_locals['help'] = Helper()
    base_locals['exit'] = sys.exit

    sys.ps1 = 'TAS>>>\t'
    sys.ps2 = '......\t'
    code.interact(banner=banner, local=base_locals)


if __name__ == '__main__':
    tas_console()
