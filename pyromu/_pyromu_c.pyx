# cython: language_level = 3, free_threaded=True, cdivision=True

from array import array
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.time cimport monotonic_ns

from cpython.array cimport array
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

cimport cython

cdef extern from "_romu.h":

    # # Shortcut of _PyLong_AsByteArray but simplified
    # object PyRomuLong_AsByteArray(unsigned char* data, Py_ssize_t size)
    object PyRomu_getrandbits_uint32(
        uint32_t* state, 
        uint64_t k, 
        uint32_t (*genrand_cb)(uint32_t* state) noexcept nogil
    ) # type: ignore (Silly cyright)

    object PyRomu_randbytes_uint32(
        uint32_t* state, 
        uint64_t k, 
        uint32_t (*genrand_cb)(uint32_t* state) noexcept nogil
    ) # type: ignore (Silly cyright)

    object PyRomu_getrandbits_uint64(
        uint64_t* state, 
        uint64_t k, 
        uint64_t (*genrand_cb)(uint64_t* state) noexcept nogil
    ) # type: ignore (Silly cyright)
    
    object PyRomu_randbytes_uint64(
        uint64_t* state, 
        uint64_t k, 
        uint64_t (*genrand_cb)(uint64_t* state) noexcept nogil
    ) # type: ignore (Silly cyright)

    uint64_t splitMix64(uint64_t) noexcept nogil
    uint32_t splitMix32(uint32_t) noexcept nogil
    uint64_t romuQuad_random(uint64_t*) noexcept nogil
    uint64_t romuTrio_random(uint64_t*) noexcept nogil
    uint64_t romuDuo_random(uint64_t*) noexcept nogil
    uint64_t romuDuoJr_random(uint64_t*) noexcept nogil
    uint32_t romuQuad32_random(uint32_t*) noexcept nogil
    uint32_t romuTrio32_random(uint32_t*) noexcept nogil
    
    # It's Faster to try and do these in Pure C
    int setstate_uint32(uint32_t *c_state, const Py_ssize_t size , object state) except -1
    int setstate_uint64(uint64_t *c_state, const Py_ssize_t size , object state) except -1
    tuple getstate_uint32(uint32_t* c_state, const Py_ssize_t size)
    tuple getstate_uint64(uint64_t* c_state, const Py_ssize_t size)

    int seed_uint32(uint32_t* c_state, const Py_ssize_t size, object seed)
    int seed_uint64(uint64_t* c_state, const Py_ssize_t size, object seed)





@cython.internal
cdef class Romu64:
    cdef public object gauss_next
    def __init__(self, object seed = None) -> None:
        self.seed(seed)
        self.gauss_next = None
    cpdef object seed(self, object n = None):
        pass

    cpdef uint64_t getrand(self) noexcept:
        return 0

    cpdef object random(self):
        # based off mt19937-64.c
        return ((self.getrand() >> 11) * (1.0 / 9007199254740992.0))

    cpdef object getrandbits(self, uint64_t k):
        """getrandbits(k) -> x. Generates an int with k random bits."""
        return 0

    # instead of trying reverse conversions which is a waste of time
    # try instead doing the same function from above but with one step removed

    cpdef object randbytes(self, uint64_t k):
        return b""

    

cdef class RomuQuad(Romu64):
    """
    More robust than anyone could need, but uses more registers than RomuTrio.
    Est. capacity >= 2^90 bytes. Register pressure = 8 (high). State size = 256 bits.
    """
    cdef uint64_t _state[4]

    cpdef object setstate(self, state):
        if setstate_uint64(self._state, 4, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint64(self._state, 2)

    cpdef object seed(self, object n = None):
        if seed_uint64(self._state, 4, n) < 0:
            raise

    cpdef uint64_t getrand(self) noexcept:
        return romuQuad_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint64(self._state, k, romuQuad_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint64(self._state, k * 8, romuQuad_random)
    



cdef class RomuTrio(Romu64):
    """
    Great for general purpose work, including huge jobs.
    Est. capacity = 2^75 bytes. Register pressure = 6. State size = 192 bits.
    """

    cdef uint64_t _state[3]

    cpdef object setstate(self, state):
        if setstate_uint64(self._state, 3, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint64(self._state, 3)

    cpdef object seed(self, object n = None):
        if seed_uint64(self._state, 3, n) < 0:
            raise

    cpdef uint64_t getrand(self) noexcept:
        return romuTrio_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint64(self._state, k, romuTrio_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint64(self._state, k * 8, romuTrio_random)
     


cdef class RomuDuo(Romu64):
    """
    Might be faster than RomuTrio due to using fewer registers, but might struggle with massive jobs.
    Est. capacity = 2^61 bytes. Register pressure = 5. State size = 128 bits.
    """

    cdef uint64_t _state[2]

    cpdef object setstate(self, state):
        if setstate_uint64(self._state, 2, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint64(self._state, 2)

    cpdef object seed(self, object n = None):
        if seed_uint64(self._state, 2, n) < 0:
            raise

    cpdef uint64_t getrand(self) noexcept:
        return romuDuo_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint64(self._state, k, romuDuo_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint64(self._state, k * 8, romuDuo_random)
     

cdef class RomuDuoJr(Romu64):
    """
    The fastest generator using 64-bit arith., but not suited for huge jobs.
    Est. capacity = 2^51 bytes. Register pressure = 4. State size = 128 bits.
    """
    cdef uint64_t _state[2]

    cpdef object setstate(self, state):
        if setstate_uint64(self._state, 2, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint64(self._state, 2)

    cpdef object seed(self, object n = None):
        if seed_uint64(self._state, 2, n) < 0:
            raise

    cpdef uint64_t getrand(self) noexcept:
        return romuDuoJr_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint64(self._state, k, romuDuoJr_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint64(self._state, k * 8, romuDuoJr_random)
    

# 32 Bit versions
@cython.internal
cdef class Romu32:
    cdef public object gauss_next

    def __init__(self, object seed = None) -> None:
        self.seed(seed)

    cpdef object seed(self, object n = None):
        pass

    cpdef uint32_t getrand(self) noexcept:
        return 0

    cpdef object setstate(self, state):
        pass 

    cpdef object getstate(self):
        pass

    def random(self) -> float:
        # based off python's standard library (aka mt19937 32-bit )
        cdef uint32_t a = (self.getrand() >> 5)
        cdef uint32_t b = (self.getrand() >> 6)
        return  (a * 67108864.0 + b) * (1.0 / 9007199254740992.0)

    cpdef object getrandbits(self, uint64_t k):
        """getrandbits(k) -> x. Generates an int with k random bits."""
        return 0

    # instead of trying reverse conversions which is a waste of time
    # try instead doing the same function from above but with one step removed

    cpdef object randbytes(self, uint64_t k):
        return b""
    

cdef class RomuQuad32(Romu32):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """

    cdef uint32_t _state[4]

    cpdef object setstate(self, state):
        if setstate_uint32(self._state, 4, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint32(self._state, 4)

    cpdef object seed(self, object n = None):
        if seed_uint32(self._state, 4, n) < 0:
            raise

    cpdef uint32_t getrand(self) noexcept:
        return romuQuad32_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint32(self._state, k, romuQuad32_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint32(self._state, k * 4, romuQuad32_random)
    
    


cdef class RomuTrio32(Romu32):
    """
    32-bit arithmetic: Good for general purpose use, except for huge jobs.
    Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.
    """
    cdef uint32_t _state[3]

    cpdef object setstate(self, state):
        if len(state) != 3:
            raise TypeError(f"state is the wrong size expected 3 got {len(state)}")
        if setstate_uint32(self._state, 3, state) < 0:
            raise

    cpdef object getstate(self):
        return getstate_uint32(self._state, 3)

    cpdef object seed(self, object n = None):
        if seed_uint32(self._state, 3, n) < 0:
            raise

    cpdef uint32_t getrand(self) noexcept:
        return romuTrio32_random(self._state)

    cpdef object getrandbits(self, uint64_t k):
        return PyRomu_getrandbits_uint32(self._state, k, romuQuad32_random)
    
    cpdef object randbytes(self, uint64_t k):
        return PyRomu_randbytes_uint32(self._state, k * 4, romuQuad32_random)
    

cdef class RomuMono32(Romu32):
    """
    32-bit arithmetic: Suitable only up to 2^26 output-values. Outputs 16-bit numbers.
    Fixed period of (2^32)-47. Must be seeded using the romuMono32_init function.
    Capacity = 2^27 bytes. Register pressure = 2. State size = 32 bits.
    """

    cdef uint32_t _state


    cpdef object getstate(self):
        return (self._state,)

    cpdef setstate(self, state):
        setstate_uint32(&self._state, 1, state)

    cpdef object seed(self, object n = None):
        cdef Py_ssize_t i
        if n is None:
            seed = <uint32_t>monotonic_ns()
        else:
            seed = <uint32_t>hash(n)
        self._state = <uint32_t>((seed & 0x1FFFFFFF) + 1156979152)

    cpdef uint32_t getrand(self) noexcept:
        cdef uint32_t result = self._state >> 16
        self._state = (self._state * 3611795771)
        self._state = ((self._state << 12) | (self._state >> 20))
        return result

    cpdef object getrandbits(self, uint64_t k):
        """getrandbits(k) -> x. Generates an int with k random bits."""

        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return 0
        elif k < 16:
            return self.getrand() >> (16 - k)
        # Only perform safe division...
        words = (k - 1) / 16 + 1
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

    cpdef object randbytes(self, uint64_t k):
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        if not k:
            return b""
        # each character is 8 bits
        cdef uint32_t _k = k * 8
        if _k < 16:
            return (self.getrand() >> (16 - _k)).to_bytes(k, "little")

        # Only perform safe division...
        words = (_k - 1) / 16 + 1
        wordarray = array("H")
        for _ in range(words):
            r = self.getrand()
            if k < 16:
                r >>= 16 - k
            wordarray.append(r)
            k -= 16
        return wordarray.tobytes()
