#cython language_level=3

from gmpy2 cimport *

cdef extern from "gmp.h":
    ctypedef unsigned long long mp_limb_t
    ctypedef unsigned long long mp_bitcnt_t
    ctypedef long mp_size_t
    void mpz_init(mpz_t)
    void mpz_init2(mpz_t, mp_bitcnt_t)
    void mpz_init_set(mpz_t, const mpz_t)
    void mpz_clear(mpz_t)
    void mpz_set(mpz_t, const mpz_t)
    void mpz_mul_2exp(mpz_t, const mpz_t, mp_bitcnt_t)
    void mpz_fdiv_q_2exp(mpz_t, const mpz_t, mp_bitcnt_t)
    void mpz_and(mpz_t, const mpz_t, const mpz_t)
    void mpz_ior(mpz_t, const mpz_t, const mpz_t)
    void mpz_combit(mpz_t, mp_bitcnt_t)
    int mpz_tstbit(const mpz_t, mp_bitcnt_t)
    int mpz_cmp(const mpz_t, const mpz_t)
    mp_limb_t mpz_getlimbn(const mpz_t, mp_size_t)
