import time

from ds_tas.engine.wrapper import Hook


class TAS:
    def __init__(self):
        self.h = Hook()
        self.queue = []

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

    def execute(self, skip_wait=False):
        """
        Execute the sequence of commands that have been pushed
        to the TAS object
        """
        self.h.controller(False)
        self.h.background_input(True)

        # Make sure control is returned after completion
        try:
            igt = self.h.igt()
            if not skip_wait:
                # Sleep to make sure the first command is used
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