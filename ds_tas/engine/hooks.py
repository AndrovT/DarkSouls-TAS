"""Hook to access the memory of Dark Souls"""
from time import sleep

from ctypes import (
    windll, POINTER, pointer, Structure, sizeof, cast
)

from ctypes.wintypes import (
    BYTE, CHAR, DWORD, HMODULE, LPVOID, SIZE
)

from importlib.resources import path

from ds_tas.exceptions import GameNotRunningError

from ds_tas.engine.structures import (
    PTDERelease, TasDll
)


class MODULEENTRY32(Structure):
    _fields_ = [("dwSize", DWORD),
                ("th32ModuleID", DWORD),
                ("th32ProcessID", DWORD),
                ("GlblcntUsage", DWORD),
                ("ProccntUsage", DWORD),
                ("modBaseAddr", POINTER(BYTE)),
                ("modBaseSize", DWORD),
                ("hModule", HMODULE),
                ("szModule", CHAR*256),
                ("szExePath", CHAR*260)]


# Short aliases for kernel32 and user32 functions
ReadProcessMemory = windll.kernel32.ReadProcessMemory
WriteProcessMemory = windll.kernel32.WriteProcessMemory
OpenProcess = windll.kernel32.OpenProcess
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
Module32First = windll.kernel32.Module32First
Module32Next = windll.kernel32.Module32Next
CloseHandle = windll.kernel32.CloseHandle
TerminateProcess = windll.kernel32.TerminateProcess
GetProcAddress = windll.kernel32.GetProcAddress
VirtualAllocEx = windll.kernel32.VirtualAllocEx
GetModuleHandleA = windll.kernel32.GetModuleHandleA
CreateRemoteThread = windll.kernel32.CreateRemoteThread
LoadLibraryA = windll.kernel32.LoadLibraryA

FindWindowW = windll.user32.FindWindowW
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId


class PTDEHook:
    """
    Hook Dark Souls: Prepare To Die Edition

    Provides functions to read and write the memory of dark souls
    """
    WINDOW_NAME = "DARK SOULS"

    def __init__(self):
        self.debug = False
        self.w_handle = None
        self.process_id = None
        self.handle = None
        self.xinput_address = None

        # Actually get the hook
        self.acquire()

    def __del__(self):
        self.release()

    def acquire(self):
        """
        Acquire a hook into the game window.
        """
        self.w_handle = FindWindowW(None, self.WINDOW_NAME)
        # Error if game not found
        if self.w_handle == 0:
            raise GameNotRunningError(f"Could not find the {self.WINDOW_NAME} "
                                      f"game window. "
                                      f"Make sure the game is running.")

        self.process_id = DWORD(0)
        GetWindowThreadProcessId(self.w_handle, pointer(self.process_id))
        # Open process with PROCESS_TERMINATE, PROCESS_VM_OPERATION,
        # PROCESS_VM_READ and PROCESS_VM_WRITE access rights
        flags = 0x1 | 0x8 | 0x10 | 0x20
        self.handle = OpenProcess(flags, False, self.process_id)

        # TODO: Add a switch for debug
        self.game = PTDERelease(self.read_memory, self.write_memory)

        tas_address = self.get_module_base_address('tas.dll')
        if tas_address is None:
            with path(__package__, 'tas.dll') as p:
                self.inject_dll(str(p))
        # Wait for tas.dll to load and get base address
        while tas_address is None:
            sleep(0.1)
            tas_address = self.get_module_base_address('tas.dll')
        self.tas_dll = TasDll(tas_address, self.read_memory, self.write_memory)

        self.write_memory(
            self.game.frame_count_patch.address,
            self.game.frame_count_patch.patch(self.tas_dll.FrameCount.offset)
        )

        self.game.PresInt.value = 5

        # Hook wait function
        self.hook_wait(True)

        # Hook QueryPerformanceCounter
        '''self.write_memory(
            self.game.qpc_patch_1.address,
            self.game.qpc_patch_1.patch(self.tas_dll.qpc_hook.address)
        )'''
        '''self.write_memory(
            self.game.qpc_patch_2.address,
            self.game.qpc_patch_2.patch(self.tas_dll.qpc_hook.address)
        )'''

    def release(self):
        """
        Release the hooks
        """
        if not (self.handle or self.w_handle):
            return

        handles = [self.handle, self.w_handle]
        for handle in handles:
            try:
                # If the application is closed this will fail
                CloseHandle(handle)
            except OSError:
                pass

    def rehook(self):
        self.release()
        try:
            self.acquire()
        except OSError:
            raise GameNotRunningError(
                f"Could not acquire the TAS Hook to {self.WINDOW_NAME}. "
                "Make sure the game is running."
            )

    def check_and_rehook(self):
        """
        Check if the game is running, if not try to rehook.

        :return:
        """
        try:
            self.igt()  # TODO: Use something else than igt
        except GameNotRunningError:
            self.rehook()

    def read_memory(self, address, length):
        out = (BYTE*length)()
        ReadProcessMemory(self.handle, LPVOID(address), pointer(out),
                          SIZE(length), pointer(SIZE(0)))
        return bytes(out)

    def write_memory(self, address, data):
        ptr = pointer((BYTE*len(data))(*data))
        WriteProcessMemory(self.handle, LPVOID(address), ptr,
                           SIZE(len(data)), pointer(SIZE(0)))

    def force_quit(self):
        result = TerminateProcess(self.handle)
        if result == 0:
            print('Quit Failed')
        else:
            print('Quit Successful.')
            self.release()

    def get_module_info(self, module_name):
        lpszModuleName = module_name.encode("ascii")
        # TH32CS_SNAPMODULE and TH32CS_SNAPMODULE32
        hSnapshot = CreateToolhelp32Snapshot(0x8 | 0x10, self.process_id)
        ModuleEntry32 = MODULEENTRY32()
        ModuleEntry32.dwSize = sizeof(MODULEENTRY32)
        if Module32First(hSnapshot, pointer(ModuleEntry32)):
            while True:
                if ModuleEntry32.szModule == lpszModuleName:
                    out = ModuleEntry32
                    CloseHandle(hSnapshot)
                    return out
                if Module32Next(hSnapshot, pointer(ModuleEntry32)):
                    continue
                else:
                    CloseHandle(hSnapshot)
                    raise RuntimeError(f"Module {module_name} cannot be found")

    def get_module_base_address(self, module_name):
        try:
            info = self.get_module_info(module_name)
        except RuntimeError:
            return None
        return cast(info.modBaseAddr, LPVOID).value

    def inject_dll(self, dll_name):
        dll_name = dll_name.encode('ascii')
        remote_str = VirtualAllocEx(
            self.handle,
            LPVOID(0),
            SIZE(len(dll_name)),
            DWORD(0x00002000 | 0x00001000),
            DWORD(0x04)
        )
        self.write_memory(remote_str, dll_name)
        self.LoadLib = self.game.LoadLibraryA_ptr.value
        CreateRemoteThread(
            self.handle,
            LPVOID(0),
            SIZE(0),
            self.LoadLib,
            LPVOID(remote_str),
            DWORD(0),
            DWORD(0)
        )

    def write_input(self, input_state, force=False):
        """Sends input state to the game"""
        assert self.mode == "tas_input"
        if not force:
            while not self.tas_dll.Sync.value:
                pass

        self.tas_dll.input_state.value = input_state

        self.tas_dll.Sync.value = False

    def next(self):
        assert self.mode == "custom"
        while self.tas_dll.WaitFlag.value != 2:
            pass
        self.tas_dll.WaitFlag.value = 1

    def hook_wait(self, state):
        if state:
            self.write_memory(
                self.game.wait_hook.address,
                self.game.wait_hook.patch(self.tas_dll.wait_hook.value)
            )
            self.write_memory(self.game.no_skip.address, self.game.no_skip.patch)
        else:
            self.write_memory(self.game.wait_hook, self.game.wait_hook.orig)
            if self.tas_dll.wait_flag.value == 2:
                self.tas_dll.wait_flag.value = 1

    def set_mode(self, mode):
        """ mode:
        default
        tas_input
        """
        if mode == "default":
            # Disable background input
            self.write_memory(
                self.game.background_input.address,
                self.game.background_input.orig
            )

            # Unhook GetInputState
            self.write_memory(
                self.game.get_input_hook.address,
                self.game.get_input_hook.orig
            )

            # Unhook mouse input
            self.write_memory(
                self.game.mouse_input_hook.address,
                self.game.mouse_input_hook.orig
            )
            self.write_memory(
                self.game.frgp_mouse_hook.address,
                self.game.frgp_mouse_hook.orig
            )

            self.tas_dll.Mode.value = 0
            self.tas_dll.Sync.value = False
        elif mode == "tas_input":
            self.tas_dll.Mode.value = 1
            self.tas_dll.Sync.value = True

            # Hook mouse input
            self.write_memory(
                self.game.mouse_input_hook.address,
                self.game.mouse_input_hook.patch(self.tas_dll.mouse_input_hook.value)
            )
            self.write_memory(
                self.game.frgp_mouse_hook.address,
                self.game.frgp_mouse_hook.patch(self.tas_dll.frgp_mouse_hook.value)
            )

            # Hook GetInputState
            self.write_memory(
                self.game.get_input_hook.address,
                self.game.get_input_hook.patch(self.tas_dll.get_input_hook.value)
            )

            # Enable background input
            self.write_memory(self.game.background_input.address,
                              self.game.background_input.patch)
        self.mode = mode

    def set_frame_time(self, frame_time):
        """frame_time: desired minimum frame time in seconds
        """
        self.tas_dll.FrameTime.value = frame_time

    def qpc_patch(self):
        self.write_memory(
            self.game.qpc_patch_2.address,
            self.game.qpc_patch_2.patch(self.tas_dll.qpc_hook.address)
        )
