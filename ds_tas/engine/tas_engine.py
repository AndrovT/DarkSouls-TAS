import time
from contextlib import contextmanager

from ds_tas.engine.wrapper import Hook


class TAS:
    def __init__(self):
        self.h = Hook()
        self.queue = []

    def igt(self):
        """
        Get the raw in game time (alias for h.igt)

        :return: In game time in ms(?)
        """
        return self.h.igt()

    def clear(self):
        """
        Clear the keypress queue
        """
        self.queue.clear()

    def push(self, i):
        """
        Add an input to the queue
        Expects a list of 20 integers.

        Or a Keypress or a KeySequence

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
        if isinstance(i[0], list) and len(i[0]) == 20:
            self.queue.extend(i)
        elif isinstance(i[0], int) and len(i) == 20:
            self.queue.append(i)
        else:
            raise ValueError(f'Invalid Input: {i}')

    @contextmanager
    def tas_control(self):
        """
        Give control of the game to the TAS Engine for commands and return control after.
        """
        self.h.controller(False)
        self.h.background_input(True)
        try:
            yield
        finally:
            self.h.controller(True)
            self.h.background_input(False)

    def execute(self, igt_wait=True, side_effect=None):
        """
        Execute the sequence of commands that have been pushed
        to the TAS object

        Show Commands will ignore 'wait' commands

        :param igt_wait: wait for the igt to tick before performing the first input
        :param side_effect: Call this method on each keypress if it is defined
        """
        with self.tas_control():
            igt = self.igt()
            if igt_wait:
                # Wait for IGT to tick before running the first input
                while igt == self.igt():
                    time.sleep(0.002)
            else:
                # If not waiting for IGT, sleep for 1/20th of a second
                # Otherwise the first input often gets eaten.
                time.sleep(0.05)

            # Loop over the queue and then clear it
            for command in self.queue:
                self.h.write_input(command)
                if side_effect:
                    side_effect(command)
                igt = self.igt()
                while igt == self.igt():
                    time.sleep(0.002)
            self.queue.clear()


tas = TAS()
