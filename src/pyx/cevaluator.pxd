#cython language_level=3

from gmpy2 cimport *

from cstate cimport GameTree

cdef class Eval1:
    cdef int** piece_values     # 64 x 16
    cdef mpz_t temp

    cdef evaluate(self, int n)
