from pyromu._helpers_py import (
    PyRomuDuo, 
    PyRomuDuoJr,
    # PyRomuMono32,
    PyRomuQuad,
    # PyRomuQuad32,
    PyRomuTrio,
    PyRomuTrio32
)
from pyromu._helpers_c import (
    CRomuDuo, 
    CRomuDuoJr,
    # CRomuMono32,
    CRomuQuad,
    CRomuQuad32,
    CRomuTrio,
    CRomuTrio32
)
from pyromu._base_random import RomuABC
from itertools import repeat as _repeat

import pytest

# Number of times to be ran...
N = 10


@pytest.fixture(
    params=(
        PyRomuDuo, 
        PyRomuDuoJr,
        PyRomuQuad,
        # PyRomuQuad32, Broken
        PyRomuTrio,
        PyRomuTrio32,
        CRomuDuo, 
        CRomuDuoJr,
        CRomuQuad,
        CRomuQuad32,
        CRomuTrio,
        CRomuTrio32
    )
)
def GEN(request: pytest.FixtureRequest) -> RomuABC:
    return request.param()

def _test_generator(n, func, args) -> None:
    from statistics import stdev, fmean as mean
    from time import perf_counter

    t0 = perf_counter()
    data = [func(*args) for i in _repeat(None, n)]
    t1 = perf_counter()

    xbar = mean(data)
    sigma = stdev(data, xbar)
    low = min(data)
    high = max(data)

    print(f'{t1 - t0:.3f} sec, {n} times {func.__name__}')
    print('avg %g, stddev %g, min %g, max %g\n' % (xbar, sigma, low, high))


def test_random(GEN: RomuABC, ) -> None:
    _test_generator(N, GEN.random, ())

def test_random_normalvariate(GEN: RomuABC, ) -> None:
    _test_generator(N, GEN.normalvariate, (0.0, 1.0))

def test_random_lognormvariate(GEN: RomuABC) -> None:
    _test_generator(N, GEN.lognormvariate, (0.0, 1.0))

def test_random_vonmisesvariate(GEN: RomuABC) -> None:
    _test_generator(N, GEN.vonmisesvariate, (0.0, 1.0))

def test_gammavariate(GEN: RomuABC):
    _test_generator(N, GEN.gammavariate, (0.01, 1.0))
    _test_generator(N, GEN.gammavariate, (0.1, 1.0))
    _test_generator(N, GEN.gammavariate, (0.1, 2.0))
    _test_generator(N, GEN.gammavariate, (0.5, 1.0))
    _test_generator(N, GEN.gammavariate, (0.9, 1.0))
    _test_generator(N, GEN.gammavariate, (1.0, 1.0))
    _test_generator(N, GEN.gammavariate, (2.0, 1.0))
    _test_generator(N, GEN.gammavariate, (20.0, 1.0))
    _test_generator(N, GEN.gammavariate, (200.0, 1.0))

def test_random_gauss(GEN: RomuABC):
    _test_generator(N, GEN.gauss, (0.0, 1.0))

def test_random_betavariate(GEN: RomuABC):
    _test_generator(N, GEN.betavariate, (3.0, 3.0))

def test_random_triangualr(GEN: RomuABC):
    _test_generator(N, GEN.triangular, (0.0, 1.0, 1.0 / 3.0))

