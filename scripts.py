''' Here are examples, how the tas tools can be used.
Note that the first input after loading a savefile will not be registered. '''
from ds_tas import *

global RUN
RUN = 32767
global WALK
WALK = 26500


def quitout():
    write(start=1)
    write(5)
    write(dpad_left=1)
    write(a=1)
    write()
    write(dpad_up=1)
    write(a=1)
    write()
    write(dpad_left=1)
    write(a=1)


def moveswap():
    write(l1=1)
    write(start=1)
    write(5)
    write(dpad_right=1)
    write(a=1)
    write()
    write(dpad_down=1)
    write(a=1)
    write(2)
    write(dpad_up=1)
    write(a=1)
    write(2)
    write(start=1)
    write(2)
    write(start=1)


def itemswap(walk, toggle, use):
    write(walk, l_thumb_y=WALK)
    write(x=1)
    write()
    write(dpad_down=1)
    write(toggle, l_thumb_y=RUN)
    write(dpad_right=1, l_thumb_y=RUN)
    write(use, l_thumb_y=RUN)
    write(x=1)
