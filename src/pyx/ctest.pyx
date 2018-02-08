#!python
#cython language_level=3
# distutils: libraries = gmp mpfr mpc

from gmpy2 cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Free

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
