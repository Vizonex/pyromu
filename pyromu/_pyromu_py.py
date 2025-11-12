"""Pure Python version of PyRomu"""

from array import array
from ctypes import c_double
from ctypes import c_int16 as uint16_t
from ctypes import c_uint32 as uint32_t
from ctypes import c_uint64 as uint64_t
from ctypes import sizeof
from os import urandom
from time import monotonic_ns
from typing import Hashable
from ._base_random import RomuABC, _State


# low level versions of splixmix (32 & 64)
def splitmix64(x: int) -> int:
    # it's truthy so I won't bother
    x = uint64_t(x + 0x9E3779B97F4A7C15).value
    z = uint64_t(x).value
    z = uint64_t((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9).value
    z = uint64_t((z ^ (z >> 27)) * 0x94D049BB133111EB).value
    return uint64_t(z ^ (z >> 31)).value


def splitmix32(x: int) -> int:
    x = 1664525 * (x + 314159265)  # Multiplier is from Knuth.
    z = uint32_t(x).value
    z = uint32_t((z ^ (z >> 15)) * 0x5CE4E5B9).value
    z = uint32_t((z ^ (z >> 13)) * 0x1331C1EB).value
    return uint32_t(z ^ (z >> 15)).value


class Romu64(RomuABC):
    # Going to at least try and give a tiny performance boost to pure python
    # via __slots__
    __slots__ = ("gauss_next", "_state")

    def __init__(self, seed = None):
        self.seed(seed)
        self.gauss_next = None

    def getstate(self) -> _State:
        return tuple(self._state)

    def random(self) -> float:
        # based off mt19937-64.c
        return float((self.getrand() >> 11) * c_double(1.0 / 9007199254740992.0).value)

    def getrandbits(self, k: int) -> int:
        """getrandbits(k) -> x. Generates an int with k random bits."""

        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0
        elif k < 64:
            return self.getrand() >> (64 - k)
        # Only perform safe division...
        words = (k - 1) // 64 + 1
        i = 0
        for _ in range(words):
            r = self.getrand()
            if k < 64:
                r >>= 64 - k
            i = (i << 64) | r
            k -= 64
        return i

    # instead of trying reverse conversions which is a waste of time
    # try instead doing the same function from above but with one step removed

    def randbytes(self, k: int) -> bytes:
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0

        _k = k * 8
        if _k < 64:
            return (self.getrand() >> (64 - _k)).to_bytes(k, "little")

        # Only perform safe division...
        words = (_k - 1) // 64 + 1
        wordarray = array("Q")
        for _ in range(words):
            r = self.getrand()
            if k < 64:
                r >>= 64 - k
            wordarray.append(r)
            k -= 64
        return wordarray.tobytes()


class RomuQuad(Romu64):
    """
    More robust than anyone could need, but uses more registers than RomuTrio.
    Est. capacity >= 2^90 bytes. Register pressure = 8 (high). State size = 256 bits.
    """

    def setstate(self, state):
        if len(state) != 4:
            raise TypeError(f"state is the wrong size expected 4 got {len(state)}")
        self._state = array("Q", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                # create 4 uint64_t objects...
                self._state = array("Q", urandom(sizeof(uint64_t) * 4))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                # Backdown to seeding by time
                # and then hash the number to shuffle it in better...
                self._state = array("Q")
                sm = uint64_t(hash(monotonic_ns())).value

        else:
            self._state = array("Q")
            sm = uint64_t(hash(n)).value

        for i in range(4):
            self._state[i] = sm = splitmix64(sm)

    def getrand(self) -> int:
        # Mirror of romuQuad_random() from an array
        wp, xp, yp, zp = self._state
        # uint64_t type is used for overflowing & undeflowing the same way C would do it...
        self._state[0] = uint64_t((15241094284759029579) * zp).value
        # To make things easier for beginners to take in
        # I've simplified the RTOL functions for your viewing pleasure
        # but also to attempt to make things in pure python less costly...
        self._state[1] = uint64_t(zp + ((wp << 52) | (wp >> 8))).value
        self._state[2] = uint64_t(yp - xp).value
        self._state[3] = uint64_t((self._state[2] << 19) | (self._state[2] >> 45)).value
        return xp


class RomuTrio(Romu64):
    """
    Great for general purpose work, including huge jobs.
    Est. capacity = 2^75 bytes. Register pressure = 6. State size = 192 bits.
    """

    def setstate(self, state):
        if len(state) != 3:
            raise TypeError(f"state is the wrong size expected 3 got {len(state)}")
        self._state = array("Q", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("Q", urandom(sizeof(uint64_t) * 3))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                self._state = array("Q")
                sm = uint64_t(hash(monotonic_ns())).value

        else:
            self._state = array("Q")
            sm = uint64_t(hash(n)).value

        for _ in range(3):
            sm = splitmix64(sm)
            self._state.append(sm)

    def getrand(self) -> int:
        # Mirror of romuQuad_random() from an array
        xp, yp, zp = self._state
        self._state[0] = uint64_t(15241094284759029579 * zp).value
        self._state[1] = uint64_t(yp - xp).value
        self._state[1] = uint64_t((self._state[1] << 12) | (self._state[1] >> 52)).value
        self._state[2] = uint64_t(zp - yp).value
        self._state[2] = uint64_t((self._state[2] << 44) | (self._state[2] >> 20)).value
        return xp


class RomuDuo(Romu64):
    """
    Might be faster than RomuTrio due to using fewer registers, but might struggle with massive jobs.
    Est. capacity = 2^61 bytes. Register pressure = 5. State size = 128 bits.
    """

    def setstate(self, state):
        if len(state) != 2:
            raise TypeError(f"state is the wrong size expected 2 got {len(state)}")
        self._state = array("Q", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("Q", urandom(sizeof(uint64_t) * 2))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                self._state = array("Q")
                sm = uint64_t(hash(monotonic_ns())).value

        else:
            self._state = array("Q")
            sm = uint64_t(hash(n)).value

        for _ in range(2):
            sm = splitmix64(sm)
            self._state.append(sm)

    def getrand(self) -> int:
        xp = self._state[0]
        self._state[0] = uint64_t(15241094284759029579 * self._state[1]).value
        self._state[1] = uint64_t(
            uint64_t((self._state[1] << 36) | (self._state[1] >> (28))).value
            + uint64_t((self._state[1] << 15) | (self._state[1] >> 49)).value
            - xp
        ).value
        return xp


class RomuDuoJr(Romu64):
    """
    The fastest generator using 64-bit arith., but not suited for huge jobs.
    Est. capacity = 2^51 bytes. Register pressure = 4. State size = 128 bits.
    """

    def setstate(self, state):
        if len(state) != 2:
            raise TypeError(f"state is the wrong size expected 2 got {len(state)}")
        self._state = array("Q", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("Q", urandom(sizeof(uint64_t) * 2))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                self._state = array("Q")
                sm = uint64_t(hash(monotonic_ns())).value

        else:
            self._state = array("Q")
            sm = uint64_t(hash(n)).value

        for _ in range(2):
            sm = splitmix64(sm)
            self._state.append(sm)

    def getrand(self) -> int:
        xp = self._state[0]
        self._state[0] = uint64_t(15241094284759029579 * self._state[1]).value
        self._state[1] = uint64_t(self._state[1] - xp).value
        self._state[1] = uint64_t((self._state[1] << 27) | (self._state[1] >> 37)).value
        return xp

# 32 Bit versions
class Romu32(RomuABC):
    __slots__ = ("gauss_next", "_state")
    def __init__(self, seed = None):
        self.seed(seed)
        self.gauss_next = None

    def getstate(self) -> _State:
        return tuple(self._state)

    def random(self) -> float:
        # based off python's standard library (aka mt19937 32 bit twister)
        a = uint32_t(self.getrand() >> 5).value
        b = uint32_t(self.getrand() >> 6).value
        return c_double(
            c_double(a * 67108864.0 + b).value
            * c_double(1.0 / 9007199254740992.0).value
        ).value

    def getrandbits(self, k: int) -> int:
        """getrandbits(k) -> x. Generates an int with k random bits."""

        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0
        elif k < 32:
            return self.getrand() >> (32 - k)
        # Only perform safe division...
        words = (k - 1) // 32 + 1
        i = 0
        for _ in range(words):
            r = self.getrand()
            if k < 32:
                r >>= 32 - k
            i = (i << 32) | r
            k -= 32
        return i

    # instead of trying reverse conversions which is a waste of time
    # try instead doing the same function from above but with one step removed

    def randbytes(self, k: int):
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0
        _k = k * 8
        if _k < 32:
            return (self.getrand() >> (32 - _k)).to_bytes(k, "little")

        # Only perform safe division...
        words = (_k - 1) // 32 + 1
        wordarray = array("L")
        for _ in range(words):
            r = self.getrand()
            if k < 32:
                r >>= 32 - k
            wordarray.append(r)
            k -= 32
        return wordarray.tobytes()


class RomuQuad32(Romu32):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """

    def setstate(self, state):
        if len(state) != 4:
            raise TypeError(f"state is the wrong size expected 4 got {len(state)}")
        self._state = array("L", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("L", urandom(sizeof(uint32_t) * 4))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                self._state = array("L")
                sm = uint32_t(hash(monotonic_ns())).value

        else:
            self._state = array("L")
            sm = uint32_t(hash(n)).value

        for _ in range(4):
            sm = splitmix32(sm)
            self._state.append(sm)

    def getrand(self):
        wp, xp, yp, zp = self._state
        self._state[0] = uint32_t(3323815723 * zp).value  # a-mult
        self._state[1] = uint32_t(
            zp + uint32_t((wp << 26) | (wp >> 6)).value
        ).value  # b-rotl, c-add
        self._state[2] = uint32_t(yp - xp).value  # d-sub
        self._state[3] = uint32_t(yp + wp).value  # e-add
        self._state[3] = uint32_t(
            (self._state[3] << 9) | (self._state[3] >> 22)
        ).value  # f-rotl
        return xp


class RomuTrio32(Romu32):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """

    def setstate(self, state):
        if len(state) != 3:
            raise TypeError(f"state is the wrong size expected 3 got {len(state)}")
        self._state = array("L", state)

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("L", urandom(sizeof(uint32_t) * 4))
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                self._state = array("L")
                sm = uint32_t(hash(monotonic_ns())).value

        else:
            self._state = array("L")
            sm = uint32_t(hash(n)).value

        for _ in range(4):
            sm = splitmix32(sm)
            self._state.append(sm)

    def getrand(self):
        xp = self._state[0]
        yp = self._state[1]
        zp = self._state[2]
        self._state[0] = uint32_t(3323815723 * zp).value;
        self._state[1] = uint32_t(yp - xp).value 
        self._state[1] = uint32_t((self._state[1] << 6) | (self._state[1] >> 26)).value
        self._state[2] = uint32_t(zp - yp).value 
        self._state[2] = uint32_t((self._state[1] << 22) | (self._state[1] >> 10)).value
        return xp



class RomuMono32(RomuABC):
    """
    32-bit arithmetic: Suitable only up to 2^26 output-values. Outputs 16-bit numbers.
    Fixed period of (2^32)-47. Must be seeded using the romuMono32_init function.
    Capacity = 2^27 bytes. Register pressure = 2. State size = 32 bits.
    """
    __slots__ = ("gauss_next", "_state")

    def __init__(self, seed = None):
        self.seed(seed)
        self.gauss_next = None

    def getstate(self) -> _State:
        return (self._state,)

    def setstate(self, state: _State):
        if len(state) != 1:
            raise TypeError(f"state is the wrong size expected 1 got {len(state)}")
        self._state = state[0]

    def seed(self, n: Hashable | None = None):
        if n is None:
            try:
                self._state = array("L", urandom(4))[0]
                # skip attempting to seed as array is already seeded...
                return

            except Exception:
                seed = uint32_t(hash(monotonic_ns())).value
        else:
            seed = uint32_t(hash(n)).value

        self._state = uint32_t((seed & 0x1FFFFFFF) + 1156979152).value

    def getrand(self) -> int:
        result = uint16_t(self._state >> 16).value
        self._state = uint32_t(self._state * 3611795771).value
        self._state = uint32_t((self._state << 12) | (self._state >> 20)).value
        return result

    def getrandbits(self, k: int) -> int:
        """getrandbits(k) -> x. Generates an int with k random bits."""

        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0
        elif k < 16:
            return self.getrand() >> (16 - k)
        # Only perform safe division...
        words = (k - 1) // 16 + 1
        i = 0
        for _ in range(words):
            r = self.getrand()
            if k < 16:
                r >>= 16 - k
            i = (i << 16) | r
            k -= 16
        return i

    # instead of trying reverse conversions which is a waste of time
    # try instead doing the same function from above but with one step removed

    def randbytes(self, k: int):
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return b""
        # each character is 8 bits
        _k = k * 8
        if _k < 16:
            return (self.getrand() >> (16 - _k)).to_bytes(k, "little")

        # Only perform safe division...
        words = (_k - 1) // 16 + 1
        wordarray = array("H")
        for _ in range(words):
            r = self.getrand()
            if k < 16:
                r >>= 16 - k
            wordarray.append(r)
            k -= 16
        return wordarray.tobytes()
    
    def random(self) -> float:
        # based off python's standard library (aka mt19937 32 bit twister)
        a = uint32_t(self.getrand() >> 5).value
        b = uint32_t(self.getrand() >> 6).value
        return c_double(
            c_double(a * 67108864.0 + b).value
            * c_double(1.0 / 9007199254740992.0).value
        ).value