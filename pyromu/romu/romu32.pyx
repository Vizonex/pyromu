# handles 32bit objects

@cython.no_gc_clear
cdef class RomuQuad32(PyRomu32):
    cdef:
        uint32_t wState, xState, yState, zState
    
    cdef void init_seed(self) noexcept:
        self.wState = self.seeder.Cseed()
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()
        self.zState = self.seeder.Cseed()

    cdef uint32_t getrand(self) noexcept:
        cdef uint32_t wp = self.wState, xp = self.xState, yp = self.yState, zp = self.zState
        self.wState = 3323815723u * zp;  # a-mult
        self.xState = zp + ROTL(wp,26);  # b-rotl, c-add
        self.yState = yp - xp;           # d-sub
        self.zState = yp + wp;           # e-add
        self.zState = ROTL(self.zState,9);    # f-rotl
        return xp
    
    def setstate(self, object __state):
        self.wState = PyTuple_GET_ITEM(__state, 0)
        self.xState = PyTuple_GET_ITEM(__state, 1)
        self.yState = PyTuple_GET_ITEM(__state, 2)
        self.zState = PyTuple_GET_ITEM(__state, 3)

    def getstate(self):
        return (self.wState, self.xState , self.yState, self.zState)


@cython.no_gc_clear
cdef class RomuTrio32(PyRomu32):
    cdef:
        uint32_t xState, yState, zState
    
    cdef void init_seed(self) noexcept:
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()
        self.zState = self.seeder.Cseed()

    cdef uint32_t getrand(self) noexcept:
        cdef uint32_t xp = self.xState, yp = self.yState, zp = self.zState
        self.xState = 3323815723u * zp
        self.yState = yp - xp; self.yState = ROTL(self.yState,6)
        self.zState = zp - yp; self.zState = ROTL(self.zState,22)
        return xp
    
    def setstate(self, object __state):
        self.xState = PyTuple_GET_ITEM(__state, 0)
        self.yState = PyTuple_GET_ITEM(__state, 1)
        self.zState = PyTuple_GET_ITEM(__state, 2)

    def getstate(self):
        return (self.xState , self.yState, self.zState)

