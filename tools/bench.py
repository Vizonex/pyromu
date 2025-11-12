from pyromu._helpers_py import (
    PyRomuDuo, 
    PyRomuDuoJr,
    PyRomuMono32,
    PyRomuQuad,
    PyRomuQuad32,
    PyRomuTrio,
    PyRomuTrio32
)
from pyromu._helpers_c import (
    CRomuDuo, 
    CRomuDuoJr,
    CRomuMono32,
    CRomuQuad,
    CRomuQuad32,
    CRomuTrio,
    CRomuTrio32
)
from pyromu._base_random import RomuABC
from itertools import repeat as _repeat

def _test_generator(n, func, args):
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


def _test(GEN: RomuABC, N=2000):
    print(f"=== {GEN.__class__.__name__} ===")
    _test_generator(N, GEN.random, ())
    _test_generator(N, GEN.normalvariate, (0.0, 1.0))
    _test_generator(N, GEN.lognormvariate, (0.0, 1.0))
    _test_generator(N, GEN.vonmisesvariate, (0.0, 1.0))
    _test_generator(N, GEN.gammavariate, (0.01, 1.0))
    _test_generator(N, GEN.gammavariate, (0.1, 1.0))
    _test_generator(N, GEN.gammavariate, (0.1, 2.0))
    _test_generator(N, GEN.gammavariate, (0.5, 1.0))
    _test_generator(N, GEN.gammavariate, (0.9, 1.0))
    _test_generator(N, GEN.gammavariate, (1.0, 1.0))
    _test_generator(N, GEN.gammavariate, (2.0, 1.0))
    _test_generator(N, GEN.gammavariate, (20.0, 1.0))
    _test_generator(N, GEN.gammavariate, (200.0, 1.0))
    _test_generator(N, GEN.gauss, (0.0, 1.0))
    _test_generator(N, GEN.betavariate, (3.0, 3.0))
    _test_generator(N, GEN.triangular, (0.0, 1.0, 1.0 / 3.0))

if __name__ == "__main__":
    _test(PyRomuQuad())
    _test(CRomuQuad())
    _test(PyRomuTrio())
    _test(CRomuTrio())
    _test(PyRomuDuo())
    _test(CRomuDuo())
    _test(PyRomuDuoJr())
    _test(CRomuDuoJr())

    _test(PyRomuQuad32())
    _test(CRomuQuad32())
    _test(PyRomuTrio32())
    _test(CRomuTrio32())
    # _test(PyRomuMono32())
    # _test(CRomuMono32())



