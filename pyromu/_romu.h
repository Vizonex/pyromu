/* NOTE: This code has been carefully modified from the romu library to support arrays but 
the license still remains, These functions obviously can't be done directly in cython
due to the magic required and the heavy math involved (Don't we all want performance benefits?) */

// Romu Pseudorandom Number Generators
//
// Copyright 2020 Mark A. Overton
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// ------------------------------------------------------------------------------------------------
//
// Website: romu-random.org
// Paper:   http://arxiv.org/abs/2002.11331
//
// Copy and paste the generator you want from those below.
// To compile, you will need to #include <stdint.h> and use the ROTL definition below.


#ifndef ___ROMU_H__
#define ___ROMU_H__

#ifdef __cplusplus
extern "C" {
#endif 

#include <Python.h>
#include "pythoncapi_compat.h" // For external stuff
#include <stdint.h>

#define ROTL(d,lrot) ((d<<(lrot)) | (d>>(8*sizeof(d)-(lrot))))


/* Python utilities for long conversions */

static PyObject* PyRomuLong_AsByteArray(unsigned char* data, Py_ssize_t size){
    PyObject* n = NULL;
    #if PY_VERSION_HEX < 0x030D0000
        if (_PyLong_AsByteArray((PyLongObject *)n, data, size, PY_LITTLE_ENDIAN, 0) < 0){
            return NULL;
        }
    #else
        /* it was made slightly more public in 3.13+ and it needs to match _randommodule.c's version */
        if (_PyLong_AsByteArray((PyLongObject *)n, size, PY_LITTLE_ENDIAN, 1, 1) < 0){
            return NULL;
        }
    #endif
    return n;
}

/* Same as _random_Random_genrandbits_impl but with a callback to make up for dynamic things... */
static PyObject* PyRomu_getrandbits_uint32(
    uint32_t* state, 
    uint64_t k, 
    uint32_t (*genrand_cb)(uint32_t* state)
){
    Py_ssize_t i, words;
    uint32_t r;
    uint32_t *wordarray;
    PyObject *result;

    if (k == 0)
        return PyLong_FromLong(0);

    if (k <= 32)  /* Fast path */
        return PyLong_FromUnsignedLong(genrand_cb(state) >> (32 - k));

    if ((k - 1u) / 32u + 1u > PY_SSIZE_T_MAX / 4u) {
        PyErr_NoMemory();
        return NULL;
    }
    words = (Py_ssize_t)((k - 1u) / 32u + 1u);
    wordarray = (uint32_t *)PyMem_Malloc(words * 4);
    if (wordarray == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    #if PY_LITTLE_ENDIAN
    for (i = 0; i < words; i++, k -= 32)
    #else
        for (i = words - 1; i >= 0; i--, k -= 32)
    #endif
        {
            r = genrand_cb(state);
            if (k < 32)
                r >>= (32 - k);  /* Drop least significant bits */
            wordarray[i] = r;
        }

        result = PyRomuLong_AsByteArray((unsigned char*)wordarray, words * 4);
        PyMem_Free(wordarray);
        return result;
}

/* Safest way to do recasting would be via unions so I'm not playing the don't crash the computer game */
typedef union _r64
{
    uint8_t u8[8];
    uint64_t u64;
} r64;

typedef union _r32
{
    uint8_t u8[4];
    uint64_t u32;
} r32;

/* custom and was primarly used for bypassing PyLong_AsBytearray under the assumption that
we want to prevent vulnerabilities */
static PyObject* PyRomu_randbytes_uint32(
    uint32_t* state, 
    uint64_t k, 
    uint32_t (*genrand_cb)(uint32_t* state)
){
    Py_ssize_t i, words;
    uint32_t r;
    uint32_t *wordarray;
    PyObject *result;

    if (k == 0)
        return PyBytes_FromStringAndSize(NULL, 0);

    if (k <= 32)  /* Fast path */ {
        r32 bits;
        bits.u32 = (genrand_cb(state) >> (32 - k));
        return PyBytes_FromStringAndSize((char*)bits.u8, k / 4);
    }

    if ((k - 1u) / 32u + 1u > PY_SSIZE_T_MAX / 4u) {
        PyErr_NoMemory();
        return NULL;
    }
    words = (Py_ssize_t)((k - 1u) / 32u + 1u);
    wordarray = (uint32_t *)PyMem_Malloc(words * 4);
    if (wordarray == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    #if PY_LITTLE_ENDIAN
    for (i = 0; i < words; i++, k -= 32)
    #else
        for (i = words - 1; i >= 0; i--, k -= 32)
    #endif
        {
            r = genrand_cb(state);
            if (k < 32)
                r >>= (32 - k);  /* Drop least significant bits */
            wordarray[i] = r;
        }

        result = PyBytes_FromStringAndSize((char*)wordarray, words * 4);
        PyMem_Free(wordarray);
        return result;
}

static PyObject* PyRomu_getrandbits_uint64(
    uint64_t* state, 
    uint64_t k, 
    uint64_t (*genrand_cb)(uint64_t* state)
){
    Py_ssize_t i, words;
    uint64_t r;
    uint64_t *wordarray;
    PyObject *result;

    if (k == 0)
        return PyLong_FromLong(0);

    if (k <= 64)  /* Fast path */
        return PyLong_FromUnsignedLongLong(genrand_cb(state) >> (64 - k));

    if ((k - 1u) / 64u + 1u > PY_SSIZE_T_MAX / 4u) {
        PyErr_NoMemory();
        return NULL;
    }
    words = (Py_ssize_t)((k - 1u) / 64u + 1u);
    wordarray = (uint64_t *)PyMem_Malloc(words * 8);
    if (wordarray == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    #if PY_LITTLE_ENDIAN
    for (i = 0; i < words; i++, k -= 64)
    #else
        for (i = words - 1; i >= 0; i--, k -= 64)
    #endif
        {
            r = genrand_cb(state);
            if (k < 64)
                r >>= (64 - k);  /* Drop least significant bits */
            wordarray[i] = r;
        }

        result = PyRomuLong_AsByteArray((unsigned char*)wordarray, words * 8);
        PyMem_Free(wordarray);
        return result;
}


/* custom and was primarly used for bypassing PyLong_AsBytearray under the assumption that
we want to prevent vulnerabilities */
static PyObject* PyRomu_randbytes_uint64(
    uint64_t* state, 
    uint64_t k, 
    uint64_t (*genrand_cb)(uint64_t* state)
){
    Py_ssize_t i, words;
    uint64_t r;
    uint64_t *wordarray;
    PyObject *result;

    if (k == 0)
        return PyBytes_FromStringAndSize(NULL, 0);

    if (k <= 64)  /* Fast path */ {
        r64 bits;
        bits.u64 = (genrand_cb(state) >> (32 - k));
        return PyBytes_FromStringAndSize((char*)bits.u8, k / 8);
    } 

    if ((k - 1u) / 64u + 1u > PY_SSIZE_T_MAX / 4u) {
        PyErr_NoMemory();
        return NULL;
    }
    words = (Py_ssize_t)((k - 1u) / 64u + 1u);
    wordarray = (uint64_t *)PyMem_Malloc(words * 4);
    if (wordarray == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    #if PY_LITTLE_ENDIAN
    for (i = 0; i < words; i++, k -= 64)
    #else
        for (i = words - 1; i >= 0; i--, k -= 64)
    #endif
        {
            r = genrand_cb(state);
            if (k < 64)
                r >>= (64 - k);  /* Drop least significant bits */
            wordarray[i] = r;
        }

        result = PyBytes_FromStringAndSize((char*)wordarray, words * 4);
        PyMem_Free(wordarray);
        return result;
}

/* Extra utiltities for working with tuples in CPython 
these are based off _randommodule.c but it allows for dynamic sizes
so that we don't have to repeat ourselves 6 times in a row */



static int setstate_uint32(uint32_t *c_state, const Py_ssize_t size , PyObject* state){
    Py_ssize_t i;
    uint32_t element;
    if (!PyTuple_Check(state)) {
        PyErr_SetString(PyExc_TypeError,
            "state vector must be a tuple");
        return -1;
    }
    if (PyTuple_Size(state) != size) {
        PyErr_SetString(PyExc_ValueError,
            "state vector is the wrong size");
        return -1;
    }

    for (i=0; i < size; i++) {
        if (PyLong_AsUInt32(PyTuple_GET_ITEM(state, i), &element) < 0){
            return -1;
        }
        c_state[i] = (uint32_t)element;
    }

    return 0;
}


static int setstate_uint64(uint64_t *c_state, const Py_ssize_t size , PyObject* state){
    Py_ssize_t i;
    uint64_t element;
    if (!PyTuple_Check(state)) {
        PyErr_SetString(PyExc_TypeError,
            "state vector must be a tuple");
        return -1;
    }
    if (PyTuple_Size(state) != size) {
        PyErr_SetString(PyExc_ValueError,
            "state vector is the wrong size");
        return -1;
    }

    for (i=0; i < size ; i++) {
        // This newer python function takes care of a lot of messier work for us...
        if (PyLong_AsUInt64(PyTuple_GET_ITEM(state, i), &element) < 0){
            return -1;
        }
        c_state[i] = (uint64_t)element;
    }
    return 0;
}


/* based off randommodule.c but with dynamic allocations to prevent repeating ourselves in the code*/
static PyObject* getstate_uint32(uint32_t *c_state, const Py_ssize_t size){
    PyObject* state;
    PyObject* element;
    state = PyTuple_New(size);
    if (state == NULL){
        return NULL;
    }
    for (Py_ssize_t i = 0; i < size; i++){
        element = PyLong_FromUInt32(c_state[i]);
        if ((element == NULL)){
            Py_DECREF(state);
            return NULL;
        }
    }
    return state;
}


static PyObject* getstate_uint64(uint64_t *c_state, const Py_ssize_t size){
    PyObject* state;
    PyObject* element;
    state = PyTuple_New(size);
    if (state == NULL){
        return NULL;
    }
    for (Py_ssize_t i = 0; i < size; i++){
        element = PyLong_FromUInt64(c_state[i]);
        if ((element == NULL)){
            Py_DECREF(state);
            return NULL;
        }
        PyTuple_SET_ITEM(state, i, element);
    }
    return state;
}


/* Functions were given a slight modification from the normal Splitmix functions 
in order to make them threadsafe... */ 

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

static int seed_uint32(uint32_t* c_state, const Py_ssize_t size, PyObject* seed){
    uint32_t sm;
    Py_ssize_t i;
    if (Py_IsNone(seed) || seed == NULL){
        PyTime_t now;
        if (PyTime_Monotonic(&now) < 0){
            return -1;
        }
        /* at least try and hide the time... */
        sm = splitMix32((uint32_t)(now & 0xffffffffU));
    } else {
        Py_hash_t h = PyObject_Hash(seed);
        if (h < 0){
            return -1;
        }
        sm = (uint32_t)(h);
    }
    for (i = 0; i < size; i++){
        c_state[i] = sm = splitMix32(sm);
    }
    return 0;
}

static int seed_uint64(uint64_t* c_state, const Py_ssize_t size, PyObject* seed){
    uint64_t sm;
    Py_ssize_t i;
    if (Py_IsNone(seed) || seed == NULL){
        PyTime_t now;
        if (PyTime_Monotonic(&now) < 0){
            return -1;
        }
        /* at least try and hide the time... */
        sm = splitMix64((uint64_t)(now));
    } else {
        Py_hash_t h = PyObject_Hash(seed);
        if (h < 0){
            return -1;
        }
        sm = (uint64_t)(h);
    }
    for (i = 0; i < size; i++){
        c_state[i] = sm = splitMix64(sm);
    }
    return 0;
}




#define ROTL(d,lrot) ((d<<(lrot)) | (d>>(8*sizeof(d)-(lrot))))


//===== RomuQuad ==================================================================================
//
// More robust than anyone could need, but uses more registers than RomuTrio.
// Est. capacity >= 2^90 bytes. Register pressure = 8 (high). State size = 256 bits.

uint64_t romuQuad_random (uint64_t* state) {
   uint64_t wp = state[0], xp = state[1], yp = state[2], zp = state[3];
   state[0] = 15241094284759029579u * zp; // a-mult
   state[1] = zp + ROTL(wp,52);           // b-rotl, c-add
   state[2] = yp - xp;                    // d-sub
   state[3] = yp + wp;                    // e-add
   state[3] = ROTL(state[3],19);            // f-rotl
   return xp;
}


//===== RomuTrio ==================================================================================
//
// Great for general purpose work, including huge jobs.
// Est. capacity = 2^75 bytes. Register pressure = 6. State size = 192 bits.

uint64_t romuTrio_random (uint64_t* state) {
   uint64_t xp = state[0], yp = state[1], zp = state[2];
   state[0] = 15241094284759029579u * zp;
   state[1] = yp - xp;  state[1] = ROTL(state[1],12);
   state[2] = zp - yp;  state[2] = ROTL(state[2],44);
   return xp;
}


//===== RomuDuo ==================================================================================
//
// Might be faster than RomuTrio due to using fewer registers, but might struggle with massive jobs.
// Est. capacity = 2^61 bytes. Register pressure = 5. State size = 128 bits.

uint64_t romuDuo_random (uint64_t* state) {
   uint64_t xp = state[0];
   state[0] = 15241094284759029579u * state[1];
   state[1] = ROTL(state[1],36) + ROTL(state[1],15) - xp;
   return xp;
}

//===== RomuDuoJr ================================================================================
//
// The fastest generator using 64-bit arith., but not suited for huge jobs.
// Est. capacity = 2^51 bytes. Register pressure = 4. State size = 128 bits.


uint64_t romuDuoJr_random (uint64_t *state) {
   uint64_t xp = state[0];
   state[0] = 15241094284759029579u * state[1];
   state[1] = state[1] - xp;  state[1] = ROTL(state[1],27);
   return xp;
}


//===== RomuQuad32 ================================================================================
//
// 32-bit arithmetic: Good for general purpose use.
// Est. capacity >= 2^62 bytes. Register pressure = 7. State size = 128 bits.

uint32_t romuQuad32_random (uint32_t* state) {
   uint32_t wp = state[0], xp = state[1], yp = state[2], zp = state[3];
   state[0] = 3323815723u * zp;  // a-mult
   state[1] = zp + ROTL(wp,26);  // b-rotl, c-add
   state[2] = yp - xp;           // d-sub
   state[3] = yp + wp;           // e-add
   state[3] = ROTL(state[3],9);    // f-rotl
   return xp;
}


//===== RomuTrio32 ===============================================================================
//
// 32-bit arithmetic: Good for general purpose use, except for huge jobs.
// Est. capacity >= 2^53 bytes. Register pressure = 5. State size = 96 bits.


uint32_t romuTrio32_random (uint32_t * state) {
   uint32_t xp = state[0], yp = state[1], zp = state[2];
   state[0] = 3323815723u * zp;
   state[1] = yp - xp; state[1] = ROTL(state[1],6);
   state[2] = zp - yp; state[2] = ROTL(state[2],22);
   return xp;
}


//===== RomuMono32 ===============================================================================
//
// 32-bit arithmetic: Suitable only up to 2^26 output-values. Outputs 16-bit numbers.
// Fixed period of (2^32)-47. Must be seeded using the romuMono32_init function.
// Capacity = 2^27 bytes. Register pressure = 2. State size = 32 bits.

// Moved to cython since it's small enough for that...
// void romuMono32_init (uint32_t* state, uint32_t seed) {
//    *state = (seed & 0x1fffffffu) + 1156979152u;  // Accepts 29 seed-bits.
// }

// uint16_t romuMono32_random (uint32_t* state) {
//    uint16_t result = *state >> 16;
//    *state *= 3611795771u;  *state = ROTL(*state,12);
//    return result;
// }


#ifdef __cplusplus
}
#endif 

#endif // ___ROMU_H__