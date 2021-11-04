"""Sequence creation tools for inputs.
"""
from math import sin, cos, radians
from ds_tas.sequences.basics import (
    InputState,
    Sequence,
    Chain,
    Shortest,
    Longest,
    combine_inputs,
    sequence,
    seq_factory,
    none,
    wait,
    repeat,
    wait_for,
)

# Base inputs

BUTTONS = [
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
    'mouse_1',
    'mouse_2',
    'mouse_3',
    'mouse_4',
    'mouse_5',
]


class BaseInput(InputState, Sequence):
    """Represents single frame inputs that don't change on runtime.

    Should not be used directly.
    """
    def __init__(self, **kwargs):
        InputState.__init__(self, **kwargs)
        Sequence.__init__(self)
        self.len = 1

    def __call__(self, hook):
        return (self,)

    def __repr__(self):
        res = ""
        for key in BUTTONS:
            if self._inputs[key] == 1:
                res += "&"+key
            elif self._inputs[key] == 0:
                res += "&~"+key

        if self._inputs['l_thumb_x'] is not None:
            assert self._inputs['l_thumb_y'] is not None
            res += (
                f"&LeftStick({self._inputs['l_thumb_x']}, " +
                f"{self._inputs['l_thumb_y']})"
            )
        if self._inputs['r_thumb_x'] is not None:
            assert self._inputs['r_thumb_y'] is not None
            res += (
                f"&RightStick({self._inputs['r_thumb_x']}, " +
                f"{self._inputs['r_thumb_y']})"
            )

        if self._inputs['mouse_x'] is not None:
            assert self._inputs['mouse_y'] is not None
            res += (
                f"&MouseMove({self._inputs['mouse_x']}, " +
                f"{self._inputs['mouse_y']})"
            )

        if self._inputs['scroll'] is not None:
            res += f"&Scroll({self._inputs['scroll']})"

        res = res[1:] or "wait"
        return res

    def __and__(self, other):
        if isinstance(other, BaseInput):
            return BaseInput(**combine_inputs((self, other))._inputs)
        else:
            return NotImplemented

    def __rand__(self, other):
        if isinstance(other, BaseInput):
            return BaseInput(**combine_inputs((other, self))._inputs)
        else:
            return NotImplemented


class Press(BaseInput):
    def __init__(self, key, *, state=True):
        self._state = state
        self._key = key
        super().__init__(**{key: int(state)})

    def __invert__(self):
        return Press(self._key, state=(not self._state))


up = Press("up")
down = Press("down")
left = Press("left")
right = Press("right")
start = Press("start")
select = Press("back")
l3 = Press("l_thumb")
r3 = Press("r_thumb")
l1 = Press("l1")
r1 = Press("r1")
a = Press("a")
b = Press("b")
x = Press("x")
y = Press("y")
l2 = Press("l2")
r2 = Press("r2")
m1 = Press("mouse_1")
m2 = Press("mouse_2")
m3 = Press("mouse_3")
m4 = Press("mouse_4")
m5 = Press("mouse_5")


class LeftStick(BaseInput):
    def __init__(self, x, y):
        super().__init__(l_thumb_x=x, l_thumb_y=y)


class RightStick(BaseInput):
    def __init__(self, x, y):
        super().__init__(r_thumb_x=x, r_thumb_y=y)


class MouseMove(BaseInput):
    def __init__(self, x, y):
        super().__init__(mouse_x=x, mouse_y=y)


class Scroll(BaseInput):
    def __init__(self, val):
        super().__init__(scroll=val)


no_buttons = Shortest(
    ~up,
    ~down,
    ~left,
    ~right,
    ~start,
    ~select,
    ~l3,
    ~r3,
    ~l1,
    ~r1,
    ~a,
    ~b,
    ~x,
    ~y,
    ~l2,
    ~r2,
    ~m1,
    ~m2,
    ~m3,
    ~m4,
    ~m5
)


def left_stick_rad(angle, dist):
    dist = min(max(dist, 0), 1)
    return LeftStick(
        int(sin(angle)*dist*32767),
        int(cos(angle)*dist*32767)
    )


def right_stick_rad(angle, dist):
    dist = min(max(dist, 0), 1)
    return RightStick(
        int(sin(angle)*dist*32767),
        int(cos(angle)*dist*32767)
    )


def run(angle):
    """Run in an angle

    0 degrees is straight forward
    90 degrees is right
    """
    return left_stick_rad(radians(angle), 1)


def walk(angle):
    """Walk in an angle

    0 degrees is straight forward
    90 degrees is right
    """
    return left_stick_rad(radians(angle), 0.5)


stand = LeftStick(0, 0)


def right_stick(angle, dist):
    """RightStick command from angle and distance

    0 degrees is straight forward
    90 degrees is right
    """
    return right_stick_rad(radians(angle), dist)


@seq_factory
def move_mouse_to(x_pos, y_pos):
    @sequence(1)
    def fn(hook):
        x_cur = hook.game.FrgpMouse.X.value
        y_cur = hook.game.FrgpMouse.Y.value
        return MouseMove(x_pos-x_cur, y_pos-y_cur)
    return fn


@seq_factory
def click_at(x_pos, y_pos):
    return move_mouse_to(x_pos, y_pos) & m1


@seq_factory
def arun(angle):
    """Run in an absolute angle

    Accurate to about 0.001 of a degree
    """
    angle = radians(angle)

    @sequence(1)
    def fn(hook):
        # (cos(CamAngle), 0, -sin(CamAngle))
        RotX = hook.game.Camera.Rot2D.X.value
        RotZ = hook.game.Camera.Rot2D.Z.value
        des_x = sin(angle)
        des_y = cos(angle)
        # Rotate by -CamAngle:
        # ((cos(CamAngle), -sin(CamAngle)),
        #  (sin(CamAngle), cos(CamAngle))
        # =
        # ((Rot2D.X, Rot2D.Z),
        #  (-Rot2D.Z, Rot2D.X)
        stick_x = RotX*des_x + RotZ*des_y
        stick_y = -RotZ*des_x + RotX*des_y
        return LeftStick(
            int(stick_x*32767),
            int(stick_y*32767)
        )
    return fn


@seq_factory
def awalk(angle):
    """Walk in an absulute angle

    Accurate to about 0.001 of a degree
    """
    angle = radians(angle)

    @sequence(1)
    def fn(hook):
        # (cos(CamAngle), 0, -sin(CamAngle))
        RotX = hook.game.Camera.Rot2D.X.value
        RotZ = hook.game.Camera.Rot2D.Z.value
        des_x = sin(angle)
        des_y = cos(angle)
        # Rotate by -CamAngle:
        # ((cos(CamAngle), -sin(CamAngle)),
        #  (sin(CamAngle), cos(CamAngle))
        # =
        # ((Rot2D.X, Rot2D.Z),
        #  (-Rot2D.Z, Rot2D.X)
        stick_x = RotX*des_x + RotZ*des_y
        stick_y = -RotZ*des_x + RotX*des_y
        return LeftStick(
            int(stick_x*16384),
            int(stick_y*16384)
        )
    return fn


@seq_factory
def run_to(x_pos, z_pos):
    @sequence(1)
    def fn(hook):
        PosX = hook.game.CharPosData.Pos.X.value
        PosZ = hook.game.CharPosData.Pos.Z.value

        x_delta = x_pos - PosX
        z_delta = z_pos - PosZ
        dist = (x_delta**2+z_delta**2)**(1/2)

        Rot2DX = hook.game.Camera.Rot2D.X.value
        Rot2DZ = hook.game.Camera.Rot2D.Z.value
        # Rotate by -CamAngle:
        # ((cos(CamAngle), -sin(CamAngle)),
        #  (sin(CamAngle), cos(CamAngle))
        # =
        # ((Rot2DX, Rot2DZ),
        #  (-Rot2DZ, Rot2DX)
        stick_x = (Rot2DX*x_delta + Rot2DZ*z_delta)/dist
        stick_y = (-Rot2DZ*x_delta + Rot2DX*z_delta)/dist

        return LeftStick(
            int(stick_x*32767),
            int(stick_y*32767)
        )
    return fn


@seq_factory
def walk_to(x_pos, z_pos):
    @sequence(1)
    def fn(hook):
        PosX = hook.game.CharPosData.Pos.X.value
        PosZ = hook.game.CharPosData.Pos.Z.value

        x_delta = x_pos - PosX
        z_delta = z_pos - PosZ
        dist = (x_delta**2+z_delta**2)**(1/2)

        Rot2DX = hook.game.Camera.Rot2D.X.value
        Rot2DZ = hook.game.Camera.Rot2D.Z.value
        # Rotate by -CamAngle:
        # ((cos(CamAngle), -sin(CamAngle)),
        #  (sin(CamAngle), cos(CamAngle))
        # =
        # ((Rot2DX, Rot2DZ),
        #  (-Rot2DZ, Rot2DX)
        stick_x = (Rot2DX*x_delta + Rot2DZ*z_delta)/dist
        stick_y = (-Rot2DZ*x_delta + Rot2DX*z_delta)/dist

        return LeftStick(
            int(stick_x*16384),
            int(stick_y*16384)
        )
    return fn
