#cython language_level=3

from gmpy2 cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

from gmp_funcs cimport *
from cstate cimport GameTree

cdef class Eval1:
    def __cinit__(self, object pv, int bit_turn):
        self.piece_values = <int **>PyMem_Malloc(64 * sizeof(int *))
        cdef int i, j
        for i in range(64):
            self.piece_values[i] = <int *>PyMem_Malloc(16 * sizeof(int))
            for j in range(16):
                self.piece_values[i][j] = int(pv[i][j])

        mpz_init2(self.temp, 64 + 360)

        self.bit_turn = bit_turn

    def evaluate(self, GameTree tree, int n):
        cdef int value, i, piece
        mpz_set(self.temp, tree.states[n].state)

        value = 0

        cdef mp_limb_t leastsig
        for i in range(64):
            leastsig = mpz_getlimbn(self.temp, 0)
            piece = <int>(leastsig & 0b1111)

            value += self.piece_values[i][piece]

            mpz_fdiv_q_2exp(self.temp, self.temp, 5)

        if mpz_tstbit(tree.states[n].state, self.bit_turn) == 0:
            value = -value

        tree.states[n].value = value
        tree.states[n].quality = 2

    def __dealloc__(self):
        cdef int i
        for i in range(16):
            PyMem_Free(self.piece_values[i])
        PyMem_Free(self.piece_values)

        mpz_clear(self.temp)
