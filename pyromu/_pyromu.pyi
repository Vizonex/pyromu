# Same As the _random.pyi python module
_State = tuple[int, ...]

# NOTE: States are smaller than random's version which
# is the main benefit of this library

class __PyRomuProtocol:
    """Used as a way of implementing the majority if not all base funtionality, WARNING! do not import this class"""

    def __init__(self, seed: object = ...) -> None: ...
    def seed(self, __n: object = None) -> None: ...
    def getstate(self) -> _State: ...
    def setstate(self, __state: _State) -> None: ...
    def random(self) -> float: ...
    def getrandbits(self, __k: int) -> int: ...
    def randbytes(self, n: int) -> bytes:
        """Generate n random bytes."""

class RomuQuad(__PyRomuProtocol):
    """From Romu's C Library: More robust than anyone could need, but uses more registers than RomuTrio.
    Est. capacity >= 2^90 bytes. Register pressure = 8 (high). State size = 256 bits."""

class RomuTrio(__PyRomuProtocol):
    """From Romu's C Library: Great for general purpose work, including huge jobs.
    Est. capacity = 2^75 bytes. Register pressure = 6. State size = 192 bits."""

class RomuDuo(__PyRomuProtocol):
    """From Romu's C Libary:  Might be faster than RomuTrio due to using fewer registers, but might struggle with massive jobs.
    Est. capacity = 2^61 bytes. Register pressure = 5. State size = 128 bits.
    """

class RomuDuoJr(__PyRomuProtocol):
    """From Romu's C Library: The fastest generator using 64-bit arith., but not suited for huge jobs.
    Est. capacity = 2^51 bytes. Register pressure = 4. State size = 128 bits."""

class RomuQuad32(__PyRomuProtocol):
    """From Romu's C Library: 32-bit arithmetic: Good for general purpose use.
    Est. capacity >= 2^62 bytes. Register pressure = 7. State size = 128 bits."""

class RomuTrio32(__PyRomuProtocol):
    """From Romu's C Library: 32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits."""
