import time
from contextlib import contextmanager

from ds_tas.engine.hooks import PTDEHook
from ds_tas.engine.structures import INPUT_STATE
from ..exceptions import GameNotRunningError

INPUTS = [
    'up',
    'down',
    'left',
    'right',
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
    'mouse_x',
    'mouse_y',
    'scroll',
    'mouse_1',
    'mouse_2',
    'mouse_3',
    'mouse_4',
    'mouse_5',
]


INPUT_RANGES = {
    'dpad_up': (0, 1),
    'dpad_down': (0, 1),
    'dpad_left': (0, 1),
    'dpad_right': (0, 1),
    'start': (0, 1),
    'back': (0, 1),
    'l_thumb': (0, 1),
    'r_thumb': (0, 1),
    'l1': (0, 1),
    'r1': (0, 1),
    'a': (0, 1),
    'b': (0, 1),
    'x': (0, 1),
    'y': (0, 1),
    'l2': range(0, 2**8),
    'r2': range(0, 2**8),
    'l_thumb_x': range(-2**15, 2**15),
    'l_thumb_y': range(-2**15, 2**15),
    'r_thumb_x': range(-2**15, 2**15),
    'r_thumb_y': range(-2**15, 2**15),
    'mouse_x': range(-2**31, 2**31),
    'mouse_y': range(-2**31, 2**31),
    'scroll': range(-(2**31)//120, (2**31)//120+1),
    'mouse_1': (0, 1),
    'mouse_2': (0, 1),
    'mouse_3': (0, 1),
    'mouse_4': (0, 1),
    'mouse_5': (0, 1),
}


class InputState:
    def __init__(self, **kwargs):
        self._inputs = {}
        for key in INPUTS:
            if key in kwargs:
                self._inputs[key] = kwargs[key]
            else:
                self._inputs[key] = None

    def __getattr__(self, key):
        if key in self._inputs:
            return self._inputs[key]
        else:
            raise AttributeError(f"{key} is not a input.")

    @property
    def struct(self):
        return INPUT_STATE(
            (
                (
                    self.up or 0,
                    self.down or 0,
                    self.left or 0,
                    self.right or 0,
                    self.start or 0,
                    self.back or 0,
                    self.l_thumb or 0,
                    self.r_thumb or 0,
                    self.l1 or 0,
                    self.r1 or 0,
                    0,
                    0,
                    self.a or 0,
                    self.b or 0,
                    self.x or 0,
                    self.y or 0,
                ),
                (self.l2 or 0)*255,
                (self.r2 or 0)*255,
                self.l_thumb_x or 0,
                self.l_thumb_y or 0,
                self.r_thumb_x or 0,
                self.r_thumb_y or 0,
            ),
            (
                self.mouse_x or 0,
                self.mouse_y or 0,
                (self.scroll or 0)*120,
                (self.mouse_1 or 0)*0x80,
                (self.mouse_2 or 0)*0x80,
                (self.mouse_3 or 0)*0x80,
                (self.mouse_4 or 0)*0x80,
                (self.mouse_5 or 0)*0x80,
            )
        )

    @property
    def key_list(self):
        return [self._inputs[key] for key in INPUTS]

    @classmethod
    def from_list(cls, state):
        key_values = dict(zip(INPUTS, state))
        return cls(
            **key_values
        )


class TAS:
    """
    The high level TAS engine - provides more user friendly functions
    than working directly with the hook.

    This class handles the keypresses and sequences and the command
    queue.

    Initialise with a hook to work with remaster - creating with no
    arguments will attempt to create a hook to Dark Souls PTDE.

    :param hook: TAS Hook type to hook into the game.
    """
    def __init__(self, hook=None):
        if hook is None:
            hook = PTDEHook

        self.h = hook()
        self._control_count = 0

    def igt(self):
        """
        Get the raw in game time

        :return: In game time in ms(?)
        """
        return self.h.game.igt.value

    def rehook(self):
        """
        Make the TAS Hook reconnect

        :return:
        """
        self.h.rehook()

    def check_and_rehook(self):
        """
        Check if the game is running, if not try to rehook.

        :return:
        """
        self.h.check_and_rehook()

    def force_quit(self):
        self.h.force_quit()

    def frame_count(self):
        return self.h.game.frame_count.value

    @contextmanager
    def tas_control(self):
        """
        Give control of the game to the TAS Engine for commands
        and return control after.
        """
        try:
            if self._control_count == 0:
                self.h.set_mode("tas_input")
                # Wait for a frame
                self.h.write_input(InputState().struct)
            self._control_count += 1
            yield
        except PermissionError:
            raise GameNotRunningError(
                'TAS Hook has lost connection to the game. '
                'Call tas.rehook() to reconnect.'
            )
        finally:
            self._control_count -= 1
            if self._control_count == 0:
                # Wait for a frame
                self.h.write_input(InputState().struct)
                self.h.set_mode("default")

    def _execute(self, keyseq, wait=True):
        """
        Exectutes key presses

        :param keyseq: InputState iterable
        :param wait: Wait after each frame for games update to be finished
        """
        with self.tas_control():
            time.sleep(0.1)  # Why !?!?!?!?!?
            count = self.h.tas_dll.FrameCount.value
            for input_state in keyseq:
                self.h.write_input(input_state.struct)
                if wait:
                    while count == self.h.tas_dll.FrameCount.value:
                        time.sleep(0.002)
                    count = self.h.tas_dll.FrameCount.value

    '''def keystate(self):
        """
        Get the current input state as a keypress
        :return:
        """
        state = self.h.read_input()
        return KeyPress.from_list(state)'''

    '''def record(self, start_delay=5, record_time=None, button_wait=True):
        """
        Record the inputs for a time or indefinitely

        Exit out and save by pressing start and select/back at the same time.

        use:
            >>> tas = TAS()
            >>> seq = tas.record(start_delay=10)

        playback:
            >>> tas.run(seq, start_delay=10)

        :param start_delay: Delay before recording starts in seconds
        :param record_time: Recording time
        :param button_wait: Wait for a button press to start recording
        :return: recorded tas data
        """
        print(f'Preparing to record in {start_delay} seconds')
        recording_data = []
        igt_diffs = set()

        if start_delay is None:
            start_delay = 0

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
            keypress = self.h.read_input()
            while not sum(keypress[4:6] + keypress[10:14]):
                time.sleep(0.002)
                keypress = self.h.read_input()
            print('Recording Resumed')

        while True:
            keypress = self.h.read_input()
            # Exit if start and select are held down
            if keypress[4] and keypress[5]:
                break
            recording_data.append(keypress)

            igt = self.h.igt()
            # Wait until next igt time
            while igt == self.h.igt():
                time.sleep(0.002)
            igt_diffs.add(self.h.igt() - igt)

            # Check if record time complete
            if end_time and time.clock() > end_time:
                break

        print('Recording Finished')
        print(f'Frame Lengths: {sorted(igt_diffs)}')

        recording = KeySequence.from_list(recording_data)

        return recording'''

    def run(self, keyseq, start_delay=None, igt_wait=False, display=False):
        """
        Queue up and execute a series of controller commands

        :param keyseq: Callable, returns iterable of inputs to execute
        :param start_delay: Delay before execution starts in seconds
        :param igt_wait: Wait for IGT to tick before performing the first input
        :param display: Display the game inputs as they are pressed
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

        if igt_wait:
            igt = self.igt()
            while igt == self.igt():
                time.sleep(0.002)

        self._execute(keyseq(self.h))
