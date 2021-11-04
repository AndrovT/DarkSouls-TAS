"""Provides tools for creating input sequences
"""
from math import sin, cos, radians
from functools import singledispatch
from ds_tas.sequences.basics import (
    Chain,
    Shortest,
    Longest,
    sequence,
    seq_factory,
    repeat,
    wait,
    none,
    wait_for,
)
from ds_tas.sequences.inputs import (
    a,
)


@sequence('unk')
def wait_for_igt(hook):
    igt = hook.game.igt.value
    while igt == hook.game.igt.value:
        yield wait


@sequence(0)
def zero_mouse(hook):
    hook.write(hook.game.FrgpMouse.X, 0)
    hook.write(hook.game.FrgpMouse.Y, 0)


load = Chain(
    wait_for(lambda h: h.game.igt.value == 0),
    repeat(wait+a) & wait_for_igt,
    wait_for_igt
)


@sequence(0)
def menu_kick(h):
    h.game.MenuKick.value = 2
    return ()


@seq_factory
def console_input(glob, loc):
    @sequence('unk')
    def fn(hook):
        print("Input:")
        while True:
            inp = input()
            if inp == "exit":
                return
            for input_state in eval(inp, glob, loc)(hook):
                yield input_state
    return fn


@sequence(0)
def reset_rng(hook):
    hook.game.RNG.State.A.value = 0x74915435
    hook.game.RNG.State.B.value = 0xe8353554
    return ()
