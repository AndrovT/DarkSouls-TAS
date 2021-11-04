from .sequences import *
from .engine.tas_engine import TAS
from .util import import_name


tas = TAS()


def r(seq):
    tas.run(seq)


def mouse():
    return (
        tas.h.game.FrgpMouse.X.value,
        tas.h.game.FrgpMouse.Y.value
    )

