from typing import Any
from ._pyromu import (
    RomuQuad as _RomuQuad,
    RomuTrio as _RomuTrio,
    RomuDuo as _RomuDuo,
    RomuDuoJr as _RomuDuoJr,
    RomuQuad32 as _RomuQuad32,
    RomuTrio32 as _RomuTrio32,
)
# CPython's internal Random object We will want to Override it with our own...
import _random


def install():
    """Used to replace the random module with our module..."""

