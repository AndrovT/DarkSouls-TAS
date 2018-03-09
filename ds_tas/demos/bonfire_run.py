"""
A demo of running to the first bonfire built using the basic commands.

Create a male thief character and quitout on load without touching anything else.
Move the cursor over the save file and then execute this script.

If you are running at 30FPS (and haven't inverted your controls)
it should make it to the bonfire.
"""

from ds_tas.basics import *
from ds_tas.controller import KeySequence
from ds_tas.scripts.menus import quitout, joy

bonfire_run = KeySequence([
    # Open Savefile
    a,

    # Wait for initial animation
    waitfor(90),

    # Pick up Key
    runfor(20),
    a & aim_left,
    aim_left * 9,
    s_aim_left * 2,

    # Open Cell Door
    runfor(60),
    a,
    waitfor(60),
    s_aim_left,

    # Run through first corridor
    sprintfor(300),
    a,
    runfor(60),

    # End room
    sprintfor(29),
    aim_right * 16,
    sprintfor(25),
    aim_left * 16,
    sprintfor(30),
    aim_right * 18,
    runfor(72),

    # Ladder
    wait,
    a,
    runfor(150),

    # Doorway
    aim_right * 16,
    runfor(30),

    # Turn the corner
    (run & s_aim_left) * 75,

    # Bonfire sprint
    runfor(45),

    # Light it up!
    a,

    # Victory dance
    waitfor(150),
    b,
    s_aim_right * 60,
    b,
    s_aim_right * 60,
    joy,
    waitfor(120),

    # Bye!
    quitout,
])

if __name__ == '__main__':
    bonfire_run.execute(igt_wait=False)
