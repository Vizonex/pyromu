# Handles 64 bit objects

@cython.no_gc_clear
cdef class RomuQuad(PyRomu64):
    cdef:
        uint64_t wState, xState, yState, zState
    
    cdef void init_seed(self) noexcept:
        self.wState = self.seeder.Cseed()
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()
        self.zState = self.seeder.Cseed()

    cdef uint64_t getrand(self) noexcept:
        cdef uint64_t wp = self.wState, xp = self.xState, yp = self.yState, zp = self.zState
        self.wState = 15241094284759029579u * zp # a-mult
        self.xState = zp + ROTL(wp, 52)          # b-rotl, c-add
        self.yState = yp - xp                    # d-sub
        self.zState = yp + wp                    # e-add
        self.zState = ROTL(self.zState,19)       # f-rotl
        return xp
    
    def setstate(self, object __state):
        self.wState = PyTuple_GET_ITEM(__state, 0)
        self.xState = PyTuple_GET_ITEM(__state, 1)
        self.yState = PyTuple_GET_ITEM(__state, 2)
        self.zState = PyTuple_GET_ITEM(__state, 3)

    def getstate(self):
        return (self.wState, self.xState , self.yState, self.zState)




@cython.no_gc_clear
cdef class RomuTrio(PyRomu64):
    cdef:
        uint64_t xState, yState, zState
    
    cdef void init_seed(self) noexcept:
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()
        self.zState = self.seeder.Cseed()

    cdef uint64_t getrand(self) noexcept:
        cdef uint64_t xp = self.xState, yp = self.yState, zp = self.zState
        self.xState = 15241094284759029579u * zp
        self.yState = yp - xp
        self.yState = ROTL(self.yState, 12)
        self.zState = zp - yp
        self.zState = ROTL(self.zState, 44)
        return xp
    
    def setstate(self, object __state):
        self.xState = PyTuple_GET_ITEM(__state, 0)
        self.yState = PyTuple_GET_ITEM(__state, 1)
        self.zState = PyTuple_GET_ITEM(__state, 2)

    def getstate(self):
        return (self.xState , self.yState, self.zState)



@cython.no_gc_clear
cdef class RomuDuo(PyRomu64):
    cdef:
        uint64_t xState, yState, 
    
    cdef void init_seed(self) noexcept:
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()

    cdef uint64_t getrand(self) noexcept:
        cdef uint64_t xp = self.xState
        self.xState = 15241094284759029579u * self.yState
        self.yState = ROTL(self.yState, 36) + ROTL(self.yState, 15) - xp
        return xp
    
    def setstate(self, object __state):
        self.xState = PyTuple_GET_ITEM(__state, 0)
        self.yState = PyTuple_GET_ITEM(__state, 1)

    def getstate(self):
        return (self.xState , self.yState)


@cython.no_gc_clear
cdef class RomuDuoJr(PyRomu64):
    cdef:
        uint64_t xState, yState, 
    
    cdef void init_seed(self) noexcept:
        self.xState = self.seeder.Cseed()
        self.yState = self.seeder.Cseed()

    cdef uint64_t getrand(self) noexcept:
        cdef uint64_t xp = self.xState
        self.xState = 15241094284759029579u * self.yState;
        self.yState = self.yState - xp; self.yState = ROTL(self.yState,27);
        return xp
    
    def setstate(self, object __state):
        self.xState = PyTuple_GET_ITEM(__state, 0)
        self.yState = PyTuple_GET_ITEM(__state, 1)

    def getstate(self):
        return (self.xState , self.yState)





