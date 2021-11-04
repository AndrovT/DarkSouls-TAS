"""
Offsets and pointers
"""
from ctypes import (
     c_int32, c_uint32, c_float, c_bool
)
from ctypes.wintypes import (
    BYTE, SHORT, WORD, DWORD
)
from ds_tas.engine.memory_utils import (
    MemLoc, Patch, POINTER32, LPVOID32, Structure, PartStruct, AnonStructure,
    AnonPartStruct, Queue
)


def TasDll(address, read_memory, write_memory):
    return MemLoc(SharedData)(address+0x5020, read_memory, write_memory)


class Buttons(Structure):
    _fields_ = [
        ('Up', WORD, 1),
        ('Down', WORD, 1),
        ('Left', WORD, 1),
        ('Right', WORD, 1),
        ('Start', WORD, 1),
        ('Back', WORD, 1),
        ('LeftThumb', WORD, 1),
        ('RightThumb', WORD, 1),
        ('LeftShoulder', WORD, 1),
        ('RightShoulder', WORD, 1),
        ('', WORD, 1),
        ('', WORD, 1),
        ('A', WORD, 1),
        ('B', WORD, 1),
        ('X', WORD, 1),
        ('Y', WORD, 1),
    ]


class XINPUT_GAMEPAD(Structure):
    _fields_ = [
        ('wButtons', Buttons),
        ('bLeftTrigger', BYTE),
        ('bRightTrigger', BYTE),
        ('sThumbLX', SHORT),
        ('sThumbLY', SHORT),
        ('sThumbRX', SHORT),
        ('sThumbRY', SHORT),
    ]


class XINPUT_STATE(Structure):
    _fields_ = [
        ('dwPacketNumber', DWORD),
        ('Gamepad', XINPUT_GAMEPAD),
    ]


class MOUSE_INPUT(Structure):
    _fields_ = [
        ('XMovment', c_int32),
        ('YMovment', c_int32),
        ('Scroll', c_int32),
        ('Mouse1', BYTE),
        ('Mouse2', BYTE),
        ('Mouse3', BYTE),
        ('Mouse4', BYTE),
        ('Mouse5', BYTE),
    ]


class INPUT_STATE(Structure):
    _fields_ = [
        ('Gamepad', XINPUT_GAMEPAD),
        ('Mouse', MOUSE_INPUT)
    ]


class SharedData(Structure):
    _fields_ = [
        ('Mode', BYTE),
        ('WaitFlag', BYTE),
        ('Sync', c_bool),
        ('FrameTime', c_float),
        ('FrameCount', c_uint32),
        ('input_state', INPUT_STATE),
        ('wait_hook', LPVOID32),
        ('get_input_hook', LPVOID32),
        ('mouse_input_hook', LPVOID32),
        ('frgp_mouse_hook', LPVOID32),
        ('qpc_hook', LPVOID32),
    ]


class PTDERelease():
    def __init__(self, read, write):
        super().__init__()
        self.GameStats = MemLoc(GameStats)([0x1378700, 0x0], read, write)
        self.igt = self.GameStats.igt
        self.frame_count = MemLoc(c_uint32)([0x1378604, 0x58], read, write)
        self.Camera = MemLoc(Camera)([0x1378714, 0x80], read, write)
        self.FrgpMouse = MemLoc(FrgpMouse)([0x137CF84, 0x0], read, write)
        #  0x138189c debug
        self.ChrFollowCam = MemLoc(ChrFollowCam)([0x137D6DC, 0x3C, 0x0], read, write)
        self.CharData1 = MemLoc(CharData1)([0x137DC70, 0x4, 0x0, 0x0], read, write)
        self.CharPosData = self.CharData1.CharMapDataPtr.content.CharPosDataPtr.content
        self.RNG = MemLoc(RNG)([0x13784a0, 0x0], read, write)
        self.LoadQueues = MemLoc(POINTER32(LoadQueue)*5)([0x1376F24], read, write)

        self.MenuKick = MemLoc(DWORD)([0x13784A4, 0x0], read, write)

        self.wait_hook = Patch(
            0xBACE5C,
            b'\x60\x79\x9D\xFF',
            lambda x: (x-0xBACE5C-0x4).to_bytes(4, 'little', signed=True)
        )
        self.get_input_hook = Patch(
            0x643B5C,
            b'\xE2\x69\x47\x00',
            lambda x: (x-0x643B5C-0x4).to_bytes(4, 'little', signed=True)
        )
        self.no_skip = Patch(
            0xF8F191,
            b'\x0F\xB6\x44\x24\x1B',
            b'\xB8\x02\x00\x00\x00'
        )
        self.background_input = Patch(
            0xF72543,
            b'\x0f\x94\xc0',
            b'\xb0\x01\x90'
        )
        self.mouse_input_hook = Patch(
            0x6442E5,
            b'\x6A\x14\x50\xFF\xD2',
            lambda x: (
                b'\xE8'
                + (x-0x6442E5-0x5).to_bytes(4, 'little', signed=True)
            )
        )
        self.frgp_mouse_hook = Patch(
            0xF91876,
            b'\x51\xD9\x1C\x24\xE8\xA1\xEC\xFD\xFF',
            lambda x: (
                b'\x56\x90\x90\x90\xE8'
                + (x-0xF9187F).to_bytes(4, 'little', signed=True)
            )
        )
        self.frame_count_patch = Patch(
            0xF91976,
            b'\xC3\xCC\xCC\xCC\xCC\xCC\xCC',
            lambda x: (
                b'\xFF\x05'
                + (x).to_bytes(4, 'little', signed=True)
                + b'\xC3'
            )
        )
        self.LoadLibraryA_ptr = MemLoc(LPVOID32)(0x010CC12C, read, write)
        self.qpc_patch_1 = Patch(
            0x62E30D,
            b'\x50\xC2\x0C\x01',
            lambda x: (x).to_bytes(4, 'little', signed=False)
        )
        self.qpc_patch_2 = Patch(
            0x62E339,
            b'\x50\xC2\x0C\x01',
            lambda x: (x).to_bytes(4, 'little', signed=False)
        )
        self.PresInt = MemLoc(DWORD)(0xFFB68E, read, write)


#  Document everything because why not

class Vector3D(Structure):
    _fields_ = [
        ("X", c_float),
        ("Y", c_float),
        ("Z", c_float),
    ]


class Position(Structure):
    _fields_ = [
        ("X", c_float),
        ("Y", c_float),
        ("Z", c_float),
        ("Angle", c_float),
    ]


class Click(Structure):
    _fields_ = [
        ("Down", c_bool),
        ("Up", c_bool),
        ("Hold", c_bool),
        ("", BYTE),
        ("HoldTime", c_float),
    ]


class FrgpMouse(Structure):
    _fields_ = [
        ("", DWORD),
        ("", DWORD),
        ("Left", Click),
        ("Right", Click),
        ("Middle", Click),
        ("X", c_int32),
        ("Y", c_int32),
        ("PrevX", c_int32),
        ("PrevY", c_int32),
        ("Scroll", c_int32),
        ("PrevScroll", c_int32),
        ("Change", c_int32),
    ]


class GameOptions(PartStruct):
    _fields_ = [
        (
            "GameOptions",
            0x4,
            AnonStructure(
                ('CameraSpeed', BYTE),
                ('PadVibration', BYTE),
                ('Brightness', BYTE),
                ('SoundType', BYTE),
                ('BGMVolume', BYTE),
                ('SoundEffectVolume', BYTE),
                ('VoiceVolume', BYTE),
                ('BloodLevel', BYTE),
                ('Captions', BYTE),
                ('HUD', BYTE),
                ('CameraXReverse', BYTE),
                ('CameraYReverse', BYTE),
                ('LockOnAutoSwitch', BYTE),
                ('AutoWallRecovery', BYTE),
                ('JoinLeaderboard', BYTE),
                ('DebugRankRegisterProfileIdx', BYTE)
            )
        )
    ]


class CharPosData(PartStruct):
    _fields_ = [
        ('Angle', 0x4, c_float),
        ('Pos', 0x10, Vector3D),
    ]


class CharMapData(PartStruct):
    _fields_ = [
        ('AnimDataPtr', 0x14, LPVOID32),
        ('CharPosDataPtr', 0x1C, POINTER32(CharPosData)),
        ('CharMapFlags', 0xC4, DWORD),
        ('Warp', 0xC8, DWORD),
        ('WarpX', 0xD0, c_float),
        ('WarpY', 0xD4, c_float),
        ('WarpZ', 0xD8, c_float),
        ('WarpAngle', 0xE4, c_float),
    ]


class GameStats(PartStruct):
    _fields_ = [
        ('CharData2Ptr', 0x8, LPVOID32),
        ('GameOptionsPtr', 0x2C, POINTER32(GameOptions)),
        (
            'TendenciesPtr',
            0x38,
            POINTER32(
                AnonPartStruct(
                    ('BlackWhite', 0x8, c_float),
                    ('LeftRight', 0xC, c_float),
                )
            )
        ),
        ('ClearCount', 0x3C, c_uint32),
        ('ClearState', 0x40, c_uint32),
        ('DebugFullRecover', 0x44, c_uint32),
        ('DebugItemComplete', 0x48, c_uint32),
        ('WhiteGhostsHelped', 0x4C, c_uint32),
        ('BlackPhantomsKilled', 0x50, c_uint32),
        ('DebugTrueDeath', 0x54, c_uint32),
        ('TrueDeathCount', 0x58, c_uint32),
        ('DeathCount', 0x5C, c_uint32),
        ('igt', 0x68, c_uint32),
        ('DebugLanCutPoint', 0x6C, c_uint32),
        ('DebugLanCutPointTimer', 0x70, c_uint32),
        ('DeathState', 0x78, c_uint32),
    ]


class CharData1(PartStruct):
    _fields_ = [
        ('CharMapDataPtr',  0x28, POINTER32(CharMapData)),
        ('ChrType', 0x70, DWORD),
        ('TeamType', 0x74, DWORD),
        ('ForcePlayAnimation1', 0xFC, DWORD),
        ('CharFlags1', 0x1FC, DWORD),
        ('PlayRegion', 0x284, DWORD),
        ('HP', 0x2D4, DWORD),
        ('Stamina', 0x2E4, DWORD),
        ('CharFlags2', 0x3C4, DWORD),
        ('StoredItem', 0x628, DWORD),
    ]


class Camera(PartStruct):
    _fields_ = [
        # Unit vector, points 90 degrees to the right in the flat plane from
        # players point of view.
        ('Rot2D', 0x10, Vector3D),
        # Unit vector, points 90 degrees up from the camera
        ('Rot1', 0x20, Vector3D),
        # Unit vector, points away from the camera
        ('Rot2', 0x30, Vector3D),
        # Position of the camera
        ('Pos', 0x40, Vector3D),
    ]


class ChrFollowCam(PartStruct):
    _fields_ = [
        ('Camera1', 0x0, Camera),
        ('CameraDisplacment', 0xA0, Vector3D),  # Maybe
        ('Camera2', 0xD0, Camera),
        ('Pos', 0x100, Vector3D),
        ('ChrPos', 0x160, Vector3D),
        ('CamFulcPos', 0x170, Position*4),
        ('CamPos1', 0x1B0, Position),
        ('CamPos2', 0x1C0, Position),
        ('CamPos3', 0x1D0, Position),
        ('CamRotX', 0x210, c_float),  # in radians
        ('TrueCamRotX', 0x214, c_float),  # in radians
        ('TargetRotX', 0x220, c_float),  # in radians
        ('CamDist', 0x250, c_float),
    ]


class RNG(PartStruct):
    _fields_ = [
        (
            'State',
            0x58,
            AnonStructure(('A', DWORD), ('B', DWORD))
        ),

    ]


class LoadInfo(PartStruct):
    _fields_ = [
        ('X', 0x8, DWORD),
    ]


class FileSpec(PartStruct):
    _fields_ = [
        ('UnkPtr', 0x0, LPVOID32),
        ('NamePtr', 0x4, LPVOID32),
        ('LoadInfoPtr', 0x1c, POINTER32(LoadInfo)),
        ('Flag', 0x20, BYTE),
        ('UnkPtr', 0x24, LPVOID32),
        ('UnkPtr', 0x38, LPVOID32),
        ('UnkPtr', 0x3c, LPVOID32),
    ]


class LoadQueue(Queue):
    _fields_ = [
        ('ThreadId', 0x10, c_int32),
        ('start', 0x20, c_int32),
        ('end', 0x24, c_int32),
        ('size', 0x28, c_int32),
        ('BasePtr', 0x2c, LPVOID32),
        ('array', 0x40, POINTER32(FileSpec)*0x200),
    ]


class LoadQueueArray(PartStruct):
    """At 137B0E4 (debug)"""
    _fields_ = [
        ('Array', 0x0, POINTER32(LoadQueue)*5)
    ]
