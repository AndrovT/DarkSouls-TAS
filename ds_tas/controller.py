"""
Main controller commands for keypresses and sequences.

These are the methods behind all of the basic commands. They are also
necessary for recording and playing back inputs.
"""

import json
import time
from copy import copy
from itertools import chain

from .engine import tas
from .util import largest_val

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


class KeyPress:
    """
    Button press for a controller.

    (For most operations you should use the aliases from basics.py)

    Example usage:
        >>> sprint_10_frames = KeyPress(frames=10, l_thumb_y=32767, b=1)
        >>> sprint_10_frames.execute()

    Results of operators:
        KeyPress1 + KeyPress2 = KeySequence([KeyPress1, KeyPress2])
        KeyPress(frames=x, ...) * n = KeyPress(frames=n*x, ...)
        KeyPress1 & KeyPress2 = KeyPress1 and KeyPress2 simultaneously for the longest number of frames

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

    def __mul__(self, other):
        if isinstance(other, int):
            newframes = self.frames * other
            newpress = copy(self)
            newpress.frames = newframes
            return newpress
        else:
            raise TypeError('Can only multiply keypresses by integers')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __and__(self, other):
        """
        Combine KeyPresses

        This makes sense as an 'and' command but it's logically
        more connected to 'or'.

        For every button press take the 'largest' value
        This means for values that can be negative it will take the 'bigger' number.

        :param other: KeyPress instance to combine
        :type other: KeyPress
        :return: New Combined KeyPress
        """
        return KeyPress(
            frames=max(self.frames, other.frames),
            dpad_up=max(self.dpad_up, other.dpad_up),
            dpad_down=max(self.dpad_down, other.dpad_down),
            dpad_left=max(self.dpad_left, other.dpad_left),
            dpad_right=max(self.dpad_right, other.dpad_right),
            start=max(self.start, other.start),
            back=max(self.back, other.back),
            l_thumb=max(self.l_thumb, other.l_thumb),
            r_thumb=max(self.r_thumb, other.r_thumb),
            l1=max(self.l1, other.l1),
            r1=max(self.r1, other.r1),
            a=max(self.a, other.a),
            b=max(self.b, other.b),
            x=max(self.x, other.x),
            y=max(self.y, other.y),
            l2=max(self.l2, other.l2),
            r2=max(self.r2, other.r2),
            l_thumb_x=largest_val(self.l_thumb_x, other.l_thumb_x),
            l_thumb_y=largest_val(self.l_thumb_y, other.l_thumb_y),
            r_thumb_x=largest_val(self.r_thumb_x, other.r_thumb_x),
            r_thumb_y=largest_val(self.r_thumb_y, other.r_thumb_y),
        )

    def __len__(self):
        """
        len on a KeyPress returns the number of frames it will be held for.

        :return: frame count
        """
        return self.frames

    def __eq__(self, other):
        if isinstance(other, KeyPress):
            return self.keylist == other.keylist
        else:
            return False

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

    def execute(self, igt_wait=True, tas_instance=tas):
        tas_instance.clear()
        tas_instance.push(self.keylist)
        tas_instance.execute(igt_wait=igt_wait)


class KeySequence:
    """
    A sequence or chain of keypresses to be executed by the TAS.

    Includes methods for addition and multiplication.

    :param sequence: list of KeyPress or KeySequence objects
    """
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
        self.condense()

    def __repr__(self):
        seq = ', '.join(repr(item) for item in self._sequence)
        return f'KeySequence([{seq}])'

    def __radd__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*other._sequence, *self._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([KeyPress,  *self._sequence])
        else:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, KeySequence):
            return KeySequence([*self._sequence, *other._sequence])
        elif isinstance(other, KeyPress):
            return KeySequence([*self._sequence, other])
        else:
            return NotImplemented

    def __len__(self):
        """
        Return the number of frames in the sequence.

        Alias of .framecount

        :return: framecount
        """
        return self.framecount

    def __mul__(self, other):
        """
        Integer Multiplication of a sequence should repeat the sequence

        :param other: Number of times to perform sequence
        :return: new sequence.
        """
        if isinstance(other, int):
            return KeySequence(self._sequence * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __getitem__(self, item):
        value = self._sequence[item]
        if isinstance(value, list):
            return KeySequence(value)
        else:
            return value

    def __setitem__(self, key, value):
        self._sequence[key] = value

    @property
    def framecount(self):
        return sum(press.frames for press in self._sequence)

    @property
    def keylist(self):
        return list(chain.from_iterable(item.keylist for item in self._sequence))

    def execute(self, start_delay=None, igt_wait=True, tas_instance=tas):
        """
        Queue up and execute a series of controller commands

        :param start_delay: Delay before execution starts in seconds
        :param igt_wait: Wait for IGT to tick before performing the first input
        :param tas_instance: TAS Engine for command execution
        """
        if self._sequence:
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
            tas_instance.execute(igt_wait=igt_wait)
            print('Sequence executed')
        else:
            print('No sequence defined')

    def append(self, keypress):
        self._sequence.append(keypress)

    def extend(self, keypresses):
        self._sequence.extend(keypresses)

    def condense(self):
        """
        Reduce the keysequence to the minimum number of KeyPress instances by
        combining identical button presses into single instances with multiple
        frames.

        Do nothing if the sequence is shorter than 2 KeyPresses.
        """
        if len(self._sequence) > 1:
            newseq = []
            current_press = self._sequence[0]
            for press in self._sequence[1:]:
                if not press.keylist:
                    # Skip empty presses
                    continue
                elif press.keylist[0] == current_press.keylist[0]:
                    # Only care if the keypress uses the same keys
                    current_press.frames += press.frames
                else:
                    # If the presses are different append to our new
                    # sequence and update the current press
                    newseq.append(current_press)
                    current_press = press
            newseq.append(current_press)
            self._sequence = newseq

    def to_string(self):
        """
        Dump list data to string

        :return: list of keypress commands as a string
        """
        return json.dumps(self.keylist)

    def to_file(self, keylist_file):
        with open(keylist_file, 'w') as outdata:
            outdata.write(self.to_string())

    @classmethod
    def from_string(cls, keylist_string):
        return cls.from_list(json.loads(keylist_string))

    @classmethod
    def from_file(cls, keylist_file):
        with open(keylist_file) as indata:
            result = cls.from_list(json.load(indata))
        return result

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
        recording_data = []
        igt_diffs = set()

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

        # Special code for waiting for first input
        if first_input and button_wait:
            print('Waiting for input')
            keypress = tas_instance.h.read_input()
            while not sum(keypress[4:6] + keypress[10:14]):
                time.sleep(0.002)
                keypress = tas_instance.h.read_input()
            print('Recording Resumed')

        while True:
            keypress = tas_instance.h.read_input()
            # Exit if start and select are held down
            if keypress[4] and keypress[5]:
                break
            recording_data.append(keypress)

            igt = tas_instance.h.igt()
            # Wait until next igt time
            while igt == tas_instance.h.igt():
                time.sleep(0.002)
            igt_diffs.add(tas_instance.h.igt() - igt)

            # Check if record time complete
            if end_time and time.clock() > end_time:
                break

        print('Recording Finished')
        print(f'Frame Lengths: {sorted(igt_diffs)}')

        recording = cls.from_list(recording_data)

        return recording
