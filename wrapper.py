from ctypes import cdll
import ctypes


lib = cdll.LoadLibrary('taslib.dll')

lib.hook_new.restype = ctypes.c_void_p
lib.hook_del.argtypes = [ctypes.c_void_p]

lib.hook_read_input.argtypes = [ctypes.c_void_p, 
                                ctypes.POINTER(ctypes.c_int16)]

lib.hook_write_input.argtypes = [ctypes.c_void_p,
                                 ctypes.POINTER(ctypes.c_int16)]

lib.hook_controller.argtypes = [ctypes.c_void_p, ctypes.c_bool]

lib.hook_background_input.argtypes = [ctypes.c_void_p, ctypes.c_bool]

lib.hook_igt.restype = ctypes.c_uint32
lib.hook_igt.argtypes = [ctypes.c_void_p]

lib.hook_frame_count.restype = ctypes.c_uint32
lib.hook_frame_count.argtypes = [ctypes.c_void_p]

lib.hook_get_w_handle.restype = ctypes.c_uint32
lib.hook_get_w_handle.argtypes = [ctypes.c_void_p]


class Hook:
    def __init__(self):
        self.obj = lib.hook_new()

    def __del__(self):
        lib.hook_del(self.obj)

    def read_input(self):
        ''' Returns a list of 20 integers.
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
        19: r_thumb_y (-32,768 to 32,767) '''
        array = (ctypes.c_int16*20)()
        lib.hook_read_input(self.obj, array)
        out_list = []
        for i in array:
            out_list.append(i)
        return out_list

    def write_input(self, inputs):
        ''' Expects a list of 20 integers.
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
        19: r_thumb_y (-32,768 to 32,767) '''
        array = (ctypes.c_int16*20)(*inputs)
        lib.hook_write_input(self.obj, array)

    def controller(self, state):
        ''' if state == True -> enables controller
        if state == False -> disables controller '''
        lib.hook_controller(self.obj, state)

    def background_input(self, state):
        ''' if state == True -> enables input while the game is in backgound
        if state == False -> disables input while the game is in backgound '''
        lib.hook_background_input(self.obj, state)

    def igt(self):
        ''' returns IGT '''
        return lib.hook_igt(self.obj)

    def frame_count(self):
        ''' Returns how many frames were displayed since start of the game. '''
        return lib.hook_frame_count(self.obj)

    def w_handle(self):
        ''' Returns window handle of DARK SOULS. '''
        return lib.hook_get_w_handle(self.obj)
