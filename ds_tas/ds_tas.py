import time
from itertools import chain

from .wrapper import Hook


controller_keys = [
    'dpad_up',
    'dpad_down',
    'dpad_left',
    'dpad_right',
    'start',
    'back',
    'l_thumb',
    'r_thumb',
    'l1',
    'r1',
    'a',
    'b',
    'x',
    'y',
    'l2',
    'r2',
    'l_thumb_x',
    'l_thumb_y',
    'r_thumb_x',
    'r_thumb_y',
]


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


class KeyPress:
    def __init__(
        self,
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
        Create a new KeyPress

        :param frames: Number of frames to hold the keypress
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
        self.frames = frames
        self.dpad_up = dpad_up
        self.dpad_down = dpad_down
        self.dpad_left = dpad_left
        self.dpad_right = dpad_right
        self.start = start
        self.back = back
        self.l_thumb = l_thumb
        self.r_thumb = r_thumb
        self.l1 = l1
        self.r1 = r1
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.l2 = l2
        self.r2 = r2
        self.l_thumb_x = l_thumb_x
        self.l_thumb_y = l_thumb_y
        self.r_thumb_x = r_thumb_x
        self.r_thumb_y = r_thumb_y

    def __repr__(self):
        repr_mid = ', '.join(
            f'{key}={getattr(self, key)}'
            for key in controller_keys
            if getattr(self, key) != 0
        )
        if repr_mid:
            repr_mid = f', {repr_mid}'

        return f'KeyPress(frames={self.frames}{repr_mid})'

    def __add__(self, other):
        if isinstance(other, KeyPress):
            return KeySequence([self, other])
        elif isinstance(other, KeySequence):
            return KeySequence([self, *other._sequence])

    @classmethod
    def from_list(cls, state):
        key_values = dict(zip(controller_keys, state))
        return cls(
            frames=1,
            **key_values
        )

    @classmethod
    def from_state(cls, tas_instance=tas):
        state = tas_instance.h.read_input()
        return cls.from_list(state)

    @property
    def keylist(self):
        return [
            [
                self.dpad_up,
                self.dpad_down,
                self.dpad_left,
                self.dpad_right,
                self.start,
                self.back,
                self.l_thumb,
                self.r_thumb,
                self.l1,
                self.r1,
                self.a,
                self.b,
                self.x,
                self.y,
                self.l2,
                self.r2,
                self.l_thumb_x,
                self.l_thumb_y,
                self.r_thumb_x,
                self.r_thumb_y,
            ]
            for _ in range(self.frames)
        ]

    @property
    def button_pressed(self):
        """
        Return if an on/off button is pressed (does not include triggers)

        :return: True/False
        """
        return bool(sum([
            self.start,
            self.back,
            self.l_thumb,
            self.r_thumb,
            self.l1,
            self.r1,
            self.a,
            self.b,
            self.x,
            self.y
        ]))

    def execute(self, tas_instance=tas):
        tas_instance.clear()
        tas_instance.push(self.keylist)
        tas_instance.execute()


class KeySequence:
    def __init__(self, sequence=None):
        sequence = sequence if sequence else []
        seq = []
        for item in sequence:
            if isinstance(item, KeyPress):
                seq.append(item)
            elif isinstance(item, KeySequence):
                seq.extend(item._sequence)
            else:
                raise TypeError(
                    f'Expected KeyPress or KeySequence, found {type(item)}'
                )
        self._sequence = seq

    def __repr__(self):
        seq = ', '.join(repr(item) for item in self._sequence)
        return f'KeySequence([{seq}])'

    def __radd__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*other._sequence, *self._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([KeyPress,  *self._sequence])
        else:
            raise TypeError('unsupported operand type(s) '
                            f'for +: \'{type(self)}\' and \'{type(other)}\'')

    def __add__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*self._sequence, *other._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([*self._sequence, other])
        else:
            raise TypeError('unsupported operand type(s) '
                            f'for +: \'{type(other)}\' and \'{type(self)}\'')

    def __len__(self):
        return len(self._sequence)

    def __getitem__(self, item):
        value = self._sequence[item]
        if isinstance(value, list):
            return KeySequence(value)
        else:
            return value

    def __setitem__(self, key, value):
        self._sequence[key] = value

    @property
    def keylist(self):
        return list(chain.from_iterable(item.keylist for item in self._sequence))

    def execute(self, start_delay=None, tas_instance=tas):
        """
        Queue up and execute a series of controller commands

        :param start_delay: Delay before execution starts in seconds
        :param tas_instance:
        """
        if start_delay:
            print(f'Delaying start by {start_delay} seconds')
            if start_delay >= 5:
                time.sleep(start_delay - 5)
                for i in range(5, 0, -1):
                    print(f'{i}')
                    time.sleep(1)
            else:
                time.sleep(start_delay)
        print('Executing sequence')
        tas_instance.clear()
        tas_instance.push(self.keylist)
        tas_instance.execute()
        print('Sequence executed')

    def append(self, keypress):
        self._sequence.append(keypress)

    def extend(self, keypresses):
        self._sequence.extend(keypresses)

    @classmethod
    def from_list(cls, states):
        """
        Return the keypresses from a list of lists of press values
        :param states:
        :return:
        """
        instance = cls([KeyPress.from_list(state) for state in states])
        return instance

    @classmethod
    def record(cls, start_delay, record_time=None, button_wait=False, tas_instance=tas):
        """
        Record the inputs for a time or infinitely

        Exit out and save by pressing start and select/back at the same time.

        use:
            >>> seq = KeySequence.record(start_delay=10)

        playback:
            >>> seq.execute(start_delay=10)

        :param start_delay: Delay before recording starts in seconds
        :param record_time: Recording time
        :param button_wait: Wait for a button press to start recording
        :param tas_instance:
        :return: recorded tas data
        """
        print(f'Preparing to record in {start_delay} seconds')
        recording = cls()
        if start_delay >= 5:
            time.sleep(start_delay - 5)
            print('Countdown')
            for i in range(5, 0, -1):
                print(f'{i}')
                time.sleep(1)
        else:
            time.sleep(start_delay)

        print('Recording Started')
        start_time = time.clock()
        end_time = start_time + record_time if record_time else None
        first_input = True
        while True:
            # Special code for waiting for first input
            keypress = KeyPress.from_state(tas_instance)
            if first_input and button_wait:
                print('Waiting for input')
                while not keypress.button_pressed:
                    time.sleep(0.002)
                    keypress = KeyPress.from_state(tas_instance)
                first_input = False
                print('Recording Resumed')
            # Exit if start and select are held down
            if keypress.start and keypress.back:
                break
            recording.append(keypress)
            igt = tas_instance.h.igt()
            # Wait until next igt time
            while igt == tas_instance.h.igt():
                time.sleep(0.002)
            # Check if record time complete
            if end_time and time.clock() > end_time:
                break
        print('Recording Finished')

        return recording
