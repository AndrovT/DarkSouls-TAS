import time
from wrapper import Hook


class TAS:
    def __init__(self):
        self.h = Hook()
        self.queue = []

    def push(self, i):
        """
        Add an input to the queue
        Expects a list of 20 integers.

        index: meaning (values)
        0: dpad_up (0 or 1)
        1: dpad_down (0 or 1)
        2: dpad_left (0 or 1)
        3: dpad_right (0 or 1)
        4: start (0 or 1)
        5: back (0 or 1)
        6: left_thumb (0 or 1)
        7: right_thumb (0 or 1)
        8: left_shoulder (0 or 1)
        9: right_shoulder (0 or 1)
        10: a (0 or 1)
        11: b (0 or 1)
        12: x (0 or 1)
        13: y (0 or 1)
        14: l_trigger (0 to 255)
        15: r_trigger (0 to 255)
        16: l_thumb_x (-32,768 to 32,767)
        17: l_thumb_y (-32,768 to 32,767)
        18: r_thumb_x (-32,768 to 32,767)
        19: r_thumb_y (-32,768 to 32,767)
        """
        self.queue.append(i)

    def start(self):
        """
        Execute the sequence of commands that have been pushed
        to the TAS object
        """
        self.h.controller(False)
        self.h.background_input(True)

        # Make sure control is returned after completion
        try:
            igt = self.h.igt()
            while igt == self.h.igt():
                time.sleep(0.002)

            # Loop over the queue and clear it
            for command in self.queue:
                self.h.write_input(command)
                igt = self.h.igt()
                while igt == self.h.igt():
                    time.sleep(0.002)
            self.queue.clear()

        finally:
            self.h.controller(True)
            self.h.background_input(False)


tas = TAS()


def write(
        frames=1,
        *,
        dpad_up=0,
        dpad_down=0,
        dpad_left=0,
        dpad_right=0,
        start=0,
        back=0,
        l_thumb=0,
        r_thumb=0,
        l1=0,
        r1=0,
        a=0,
        b=0,
        x=0,
        y=0,
        l2=0,
        r2=0,
        l_thumb_x=0,
        l_thumb_y=0,
        r_thumb_x=0,
        r_thumb_y=0
):
    """
    Adds an input to the queue.

    The inputs are taken from the queue and pushed to the game
    exactly once per frame according to in game time.
    That means, that it does nothing in the main menu.
    Has one optional positional argument that specifies,
    for how many times should the input be added.

    :param frames: Number of frames to perform the action
    :param dpad_up:
    :param dpad_down:
    :param dpad_left:
    :param dpad_right:
    :param start:
    :param back:
    :param l_thumb:
    :param r_thumb:
    :param l1:
    :param r1:
    :param a:
    :param b:
    :param x:
    :param y:
    :param l2:
    :param r2:
    :param l_thumb_x:
    :param l_thumb_y:
    :param r_thumb_x:
    :param r_thumb_y:
    """

    last = [dpad_up, dpad_down, dpad_left, dpad_right,
            start, back, l_thumb, r_thumb,
            l1, r1, a, b, x, y, l2, r2,
            l_thumb_x, l_thumb_y, r_thumb_x, r_thumb_y]

    for i in range(frames):
        tas.push(last)


def start():
    """
    Starts pushing the inputs in the queue to the game.
    Disables the controller until it is finished.
    """

    tas.start()
