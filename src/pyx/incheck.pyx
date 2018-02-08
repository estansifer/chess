#!python
#cython language_level=3
# distutils: libraries = gmp mpfr mpc

from gmpy2 cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Free

# This throws an exception with no message:
# import_gmpy2()

cdef extern from "gmp.h":
    ctypedef unsigned long long mp_limb_t
    ctypedef unsigned long long mp_bitcnt_t
    ctypedef long mp_size_t
    void mpz_init(mpz_t)
    void mpz_set(mpz_t, const mpz_t)
    void mpz_clear(mpz_t)
    void mpz_fdiv_q_2exp(mpz_t, const mpz_t, mp_bitcnt_t)
    mp_limb_t mpz_getlimbn(const mpz_t, mp_size_t)
    void mpz_and(mpz_t, const mpz_t, const mpz_t)
    int mpz_cmp(const mpz_t, const mpz_t)

# cdef extern from "Python.h":
    # ctypedef struct PyObject:
        # pass

#
# Given a python list of mpz objects, allocates memory
# for and returns a C pointer to a list of mpz_t objects
# that have been initialized to the given values.
#
cdef mpz_t* allocate_mpz_list(object mpzs):
    cdef mpz_t* mpzts
    cdef int i, n
    n = len(mpzs)

    mpzts = <mpz_t *>PyMem_Malloc(n * sizeof(mpz_t))
    if not mpzts:
        raise MemoryError()

    for i in range(n):
        mpz_init(mpzts[i])
        mpz_set(mpzts[i], MPZ(mpzs[i]))

    return mpzts

cdef void free_mpz_list(mpz_t* mpzts, int n):
    cdef int i
    for i in range(n):
        mpz_clear(mpzts[i])
    PyMem_Free(mpzts)

cdef class IllegalCheck:
    cdef mpz_t** captures_rev
    cdef int* lens
    cdef int bits_king
    cdef mpz_t state
    cdef mpz_t temp1

    def __cinit__(self, object mpzss, int bits_king):
        self.captures_rev = <mpz_t **>PyMem_Malloc(64 * sizeof(mpz_t *))
        if not self.captures_rev:
            raise MemoryError()
        self.lens = <int *>PyMem_Malloc(64 * sizeof(int *))
        if not self.lens:
            raise MemoryError()

        cdef int i
        for i in range(64):
            self.lens[i] = len(mpzss[i])
            flatlist = []
            for a, b in mpzss[i]:
                flatlist.append(a)
                flatlist.append(b)
            self.captures_rev[i] = allocate_mpz_list(flatlist)

        self.bits_king = bits_king

        mpz_init(self.state)
        mpz_init(self.temp1)

    def illegal_check(self, object state):
        mpz_set(self.state, MPZ(state))
        mpz_fdiv_q_2exp(self.temp1, self.state, self.bits_king)
        cdef mp_limb_t leastsig = mpz_getlimbn(self.temp1, 0)
        cdef int king_square = <int>(leastsig & 0b111111)
        cdef int n = self.lens[king_square]
        cdef int i
        cdef mpz_t *captures_rev_square = self.captures_rev[king_square]
        for i in range(n):
            mpz_and(self.temp1, self.state, captures_rev_square[2 * i])
            if mpz_cmp(self.temp1, captures_rev_square[2 * i + 1]) == 0:
                return True
        return False

    def __dealloc__(self):
        cdef int i
        for i in range(64):
            free_mpz_list(self.captures_rev[i], self.lens[i] * 2)
        PyMem_Free(self.captures_rev)
        PyMem_Free(self.lens)
        mpz_clear(self.state)
        mpz_clear(self.temp1)

cdef class Eval1:
    cdef int* values
    cdef mpz_t state
    cdef mpz_t temp

    def __cinit__(self, object vss):
        self.values = <int *>PyMem_Malloc(64 * 32 * sizeof(int))
        cdef int i, j
        for i in range(64):
            for piece in range(32):
                self.values[64 * piece + i] = vss[piece][i]
        mpz_init(self.state)
        mpz_init(self.temp)

    def value(self, object state):
        mpz_set(self.state, MPZ(state))

        cdef mp_limb_t leastsig
        cdef int i, v
        cdef int piece
        v = 0
        for i in range(64):
            leastsig = mpz_getlimbn(self.state, 0)
            piece = <int>(leastsig & 0b11111)
            v += self.values[64 * piece + i]
            mpz_fdiv_q_2exp(self.temp, self.state, 5)
            mpz_set(self.state, self.temp)

        return v

    def __dealloc__(self):
        PyMem_Free(self.values)
        mpz_clear(self.state)
        mpz_clear(self.temp)
