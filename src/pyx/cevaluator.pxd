#cython language_level=3

from gmpy2 cimport *
from gmp_funcs cimport *

from cstate cimport GameTree

cdef class Eval1:
    cdef int** piece_values     # 64 x 16
    cdef mpz_t temp
    cdef mp_bitcnt_t bit_turn
