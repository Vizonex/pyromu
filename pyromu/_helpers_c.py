"""CPython implementation of romu random, used primarly for help with
pytests to ensure everything works correctly in both Cython and Python
"""

from ._pyromu_c import (
    RomuDuo as Duo,
    RomuDuoJr as DuoJR,
    RomuMono32 as Mono32,
    RomuQuad as Quad,
    RomuQuad32 as Quad32,
    RomuTrio as Trio,
    RomuTrio32 as Trio32,
)

from ._base_random import RomuABC


class CRomuDuo(Duo, RomuABC):
    """
    Might be faster than RomuTrio due to using fewer registers, but might struggle with massive jobs.
    Est. capacity = 2^61 bytes. Register pressure = 5. State size = 128 bits.
    """


class CRomuDuoJr(DuoJR, RomuABC):
    """
    The fastest generator using 64-bit arith., but not suited for huge jobs.
    Est. capacity = 2^51 bytes. Register pressure = 4. State size = 128 bits.
    """


class CRomuMono32(Mono32, RomuABC):
    """
    32-bit arithmetic: Suitable only up to 2^26 output-values. Outputs 16-bit numbers.
    Fixed period of (2^32)-47. Must be seeded using the romuMono32_init function.
    Capacity = 2^27 bytes. Register pressure = 2. State size = 32 bits.
    """


class CRomuQuad(Quad, RomuABC):
    """
    More robust than anyone could need, but uses more registers than RomuTrio.
    Est. capacity >= 2^90 bytes. Register pressure = 8 (high). State size = 256 bits.
    """


class CRomuQuad32(Quad32, RomuABC):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """


class CRomuTrio32(Trio32, RomuABC):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """


class CRomuTrio(Trio, RomuABC):
    """
    Great for general purpose work, including huge jobs.
    Est. capacity = 2^75 bytes. Register pressure = 6. State size = 192 bits.
    """
