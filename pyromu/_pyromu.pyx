# cython:language_level = 3
from libc.time cimport time, time_t
from libc.stdint cimport uint32_t, uint64_t , uint8_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free, PyMem_Realloc
from cpython.tuple cimport PyTuple_SET_ITEM, PyTuple_New
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
cimport cython



cdef extern from "Python.h":
    Py_hash_t PyObject_Hash(object)
    object PyTuple_GET_ITEM(object , Py_ssize_t)
    object PyLong_FromSize_t(size_t)
    object PyLong_FromLong(long)
    size_t PyLong_AsSize_t(object)
    object PyFloat_FromDouble(double)
    # This function is safe to use it's just that the author tim peters didn't want to maintian it.
    # see: https://python-list.python.narkive.com/lucGfAZD/pylong-frombytearray#
    object _PyLong_FromByteArray(const unsigned char *bytes, size_t n, int little_endian, int is_signed)
    # Macro
    int PY_LITTLE_ENDIAN


cdef extern from *:
    """
#define ROTL(d,lrot) ((d<<(lrot)) | (d>>(8*sizeof(d)-(lrot))))

/* Functions were given a slight modification in order to make them threadsafe... */ 
uint64_t splitMix64(uint64_t x) {
	uint64_t z = (x += 0x9e3779b97f4a7c15);
	z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9;
	z = (z ^ (z >> 27)) * 0x94d049bb133111eb;
	return z ^ (z >> 31);
}

uint32_t splitMix32 (uint32_t sState) {
   sState = 1664525u * (sState + 314159265u); // Multiplier is from Knuth.
   uint32_t z = sState;
   z = (z ^ (z >> 15)) * 0x5ce4e5b9u;
   z = (z ^ (z >> 13)) * 0x1331c1ebu;
   return z ^ (z >> 15);
}    
    """
    uint64_t splitMix64(uint64_t x) noexcept nogil
    uint32_t splitMix32(uint32_t sState) noexcept nogil
    # NOTE: Cython will compile ROTL Correcty even for 32 bit integers no need to edit anything!
    uint64_t ROTL(uint64_t d, uint64_t lrot) noexcept nogil



cdef class Seeder32:
    """Used to seed the random number generators"""
    cdef: 
        uint32_t state
    
    cdef void __init_by_time(self) noexcept:
        self.state = <uint32_t>(time(NULL) >> 32)

    cdef __init_by_obj(self, object obj):
        self.state = <uint32_t>(PyObject_Hash(obj) >> 32)

    def __init__(self, x = None):
        if x is None:
            self.__init_by_time()
        else:
            self.__init_by_obj(x)

    cdef uint32_t Cseed(self) noexcept:
        self.state = splitMix32(self.state)
        return self.state

    def seed(self):
        return self.Cseed()


cdef class Seeder64:
    cdef:
        uint64_t state
    
    cdef void __init_by_time(self) noexcept:
        self.state = <uint64_t>time(NULL)

    cdef __init_by_obj(self, object obj):
        self.state = <uint64_t>(PyObject_Hash(obj) >> 32)

    def __init__(self, x = None):
        if x is None:
            self.__init_by_time()
        else:
            self.__init_by_obj(x)

    cdef uint64_t Cseed(self) noexcept:
        self.state = splitMix64(self.state)
        return self.state

    def seed(self):
        return self.Cseed()



# NOTE: We're going to use preallocated bits in order to make genrandbits faster...
@cython.no_gc_clear
cdef class PyRomu32:
    cdef:
        Py_ssize_t size # Number of preallocated bits...
        uint32_t* bits
        Seeder32 seeder

    # Placeholder functions only...
    cdef uint32_t getrand(self) noexcept:
        return 0U
    
    cdef void init_seed(self) noexcept:
        return 

    def seed(self, __n: object = None):
        # override our current seed... 
        self.seeder = Seeder32(__n)
        self.init_seed()

    # used to allocate random bits to use in conversion with getrandbits...
    cdef uint32_t* loadbits(self, Py_ssize_t words):
        if self.size < words:
            self.bits = <uint32_t*>PyMem_Realloc(self.bits, self.size * 2)
            if self.bits == NULL:
                raise MemoryError
            self.size *= 2
        return self.bits

    @cython.cdivision(True)
    def random(self):
        # based off python's version 
        cdef uint32_t a = self.getrand() >> 5, b = self.getrand() >> 6
        return (a * 67108864.0 + b) * (1.0/9007199254740992.0)

    @cython.cdivision(True)
    cpdef object getrandbits(self, int k):
        "getrandbits(k) -> x. Generates an int with k random bits."

        # Based off Python's _randommodule.c
        cdef:
            int i, words
            uint32_t r
            uint32_t* wordarray
        
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        elif k == 0:
            return PyLong_FromLong(0)
        elif k <= 32:
            return self.getrand() >> (32 - k)

        words = (k - 1) / 32 + 1
        wordarray = self.loadbits(words)

        for i in range(words):
            r = self.getrand()
            if (k < 32):
                r >>= (32 - k)
            wordarray[i] = r
            k -= 32
        
        return _PyLong_FromByteArray(<unsigned char *>wordarray, words * 4, PY_LITTLE_ENDIAN, 0)

    # TODO (Vizonex) make randbytes faster as the bottleneck will be the wordarray itself....
    def randbytes(self, int n):
        """Generate n random bytes."""
        return self.getrandbits(n * 8).to_bytes(n, 'little')


    def __init__(self, object seed = None):
        self.size = 1024
        self.bits = <uint32_t*>PyMem_Malloc(self.size)
        self.seeder = Seeder32(seed)
        self.init_seed()

    def __dealloc__(self):
        PyMem_Free(self.bits)


# Special Converter type variable...
cdef union conv64_t:
    char u8[8]
    uint64_t u64




@cython.no_gc_clear
cdef class PyRomu64:
    cdef:
        Py_ssize_t size # Number of preallocated bits...
        uint64_t* bits
        Seeder64 seeder

    # Placeholder functions only...
    cdef uint64_t getrand(self) noexcept:
        return 0ULL
    
    cdef void init_seed(self) noexcept:
        return 

    def seed(self, __n: object = None):
        # override our current seed... 
        self.seeder = Seeder64(__n)
        self.init_seed()

    # used to allocate random bits to use in conversion with getrandbits...
    cdef uint64_t* loadbits(self, Py_ssize_t words):
        if self.size < words:
            self.bits = <uint64_t*>PyMem_Realloc(self.bits, words)
            if self.bits == NULL:
                raise MemoryError
            self.size = words
        return self.bits

    @cython.cdivision(True)
    def random(self):
        # based off mt19937-64.c
        return (self.getrand() >> 11) *(1.0/9007199254740992.0)

    @cython.cdivision(True)
    def getrandbits(self, int k) -> int:
        "getrandbits(k) -> x. Generates an int with k random bits."

        # Based off Python's _randommodule.c
        cdef:
            int i, words
            uint64_t r
            uint64_t* wordarray
        
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        elif k == 0:
            return PyLong_FromLong(0)
        elif k <= 64:
            return self.getrand() >> (64 - k)

        words = (k - 1) / 64 + 1
        wordarray = self.loadbits(words)

        for i in range(words):
            r = self.getrand()
            if (k < 64):
                r >>= (64 - k)
            wordarray[i] = r
            k -= 64
        
        return _PyLong_FromByteArray(<unsigned char *>wordarray, words * 8, PY_LITTLE_ENDIAN, 0)

    @cython.cdivision(True)
    def randbytes(self, int n):
        """Generate n random bytes."""
        
        # Using the same function as above it is possible to make randbytes faster by cutting out the int conversions
        cdef:
            int k , i, words
            uint64_t r
            uint64_t* wordarray
            bytes pybytes
            conv64_t conversion

        # N needs to be multiplied by 8 still...
        k = n * 8
        if k < 0:
            raise ValueError("number of bits must be non-negative")
        elif k == 0:
            return b''
        
        elif k <= 64:
            # A little bit weird but it should work fine....
            # TODO (Vizonex) see if unsigned chararcters and their bits would retained here...
            conversion.u64 = self.getrand() >> (64 - k)
            return PyBytes_FromStringAndSize(conversion.u8, n)

        words = (k - 1) / 64 + 1
        # We can load the bytes as 64bit integers to still be fast
        pybytes = PyBytes_FromStringAndSize(NULL, n)
        wordarray = <uint64_t*>PyBytes_AS_STRING(pybytes)

        for i in range(words):
            r = self.getrand()
            if (k < 64):
                r >>= (64 - k)
            wordarray[i] = r
            k -= 64
        return pybytes

    def __init__(self, object seed = None):
        self.size = 1024
        self.bits = <uint64_t*>PyMem_Malloc(self.size)
        self.seeder = Seeder64(seed)
        self.init_seed()

    def __dealloc__(self):
        PyMem_Free(self.bits)

# TODO: (Vizonex make .pxd files for these just to be more organized)
include "romu/romu64.pyx"
include "romu/romu32.pyx"
