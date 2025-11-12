# implementation is based off propcache
import os
import sys
import warnings

# I'll keep this enviornment variable from propcache
NO_EXTENSIONS = bool(os.environ.get("PYROMU_NO_EXTENSIONS"))  # type: bool
if sys.implementation.name != "cpython":
    NO_EXTENSIONS = True


# Seperate files were made (incase pickling is a concern)
if NO_EXTENSIONS:
    from ._helpers_py import (
        PyRomuDuo as RomuDuo,
        PyRomuDuoJr as RomuDuoJr,
        PyRomuMono32 as RomuMono32,
        PyRomuQuad as RomuQuad,
        PyRomuQuad32 as RomuQuad32,
        PyRomuTrio as RomuTrio,
        PyRomuTrio32 as RomuTrio32,
    )
else:
    try:
        from ._helpers_c import (
            CRomuDuo as RomuDuo,
            CRomuDuoJr as RomuDuoJr,
            CRomuMono32 as RomuMono32,
            CRomuQuad as RomuQuad,
            CRomuQuad32 as RomuQuad32,
            CRomuTrio as RomuTrio,
            CRomuTrio32 as RomuTrio32,
        )
    except ModuleNotFoundError:
        # Fallback
        warnings.warn(
            "Failed to import pyromu._helpers_c "
            "(Likely because it wasn't compiled), "
            "falling back to _helpers_py"
        )
        from ._helpers_py import (
            PyRomuDuo as RomuDuo,
            PyRomuDuoJr as RomuDuoJr,
            PyRomuMono32 as RomuMono32,
            PyRomuQuad as RomuQuad,
            PyRomuQuad32 as RomuQuad32,
            PyRomuTrio as RomuTrio,
            PyRomuTrio32 as RomuTrio32,
        )

__all__ = (
    "RomuDuo",
    "RomuDuoJr",
    "RomuMono32",
    "RomuQuad",
    "RomuQuad32",
    "RomuTrio",
    "RomuTrio32",
)
