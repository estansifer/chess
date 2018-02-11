#cython language_level=3

from gmpy2 cimport *
from gmp_funcs cimport *

# An instance of this class checks for whether a specific color king is in check
# (or is illegally capturable)
cdef class Check:
    cdef mpz_t* captures_rev
    cdef int* indices
    cdef mp_bitcnt_t bits_king
    cdef mp_bitcnt_t bit_turn
    cdef mpz_t state
    cdef mpz_t temp

    cdef illegal_check_c(self, mpz_t state)
    cdef in_check_c(self, mpz_t state)
    cdef can_take_king(self)

# An instance of this class represents a specific possible move, and
# can check whether that move is legal in a specified position, including
# checking for going into an illegal check.
cdef class MoveNoCheck:
    cdef int num_captures
    cdef mpz_t* captures
    cdef mpz_t check_mask
    cdef mpz_t check_result
    cdef mpz_t set_and
    cdef mpz_t set_or
    cdef mpz_t result
    cdef mpz_t temp

    cdef int move(self, mpz_t state)

# An instance of this class represents one of the four possible castling moves
cdef class CastleMove:
    cdef MoveNoCheck castle
    cdef MoveNoCheck move_int1
    cdef MoveNoCheck move_int2
    cdef mpz_t state
    cdef mpz_t result

    cdef int move(self, mpz_t state)

# An instance of this class represents all possible legal moves of one color in chess,
# excluding castling moves.
cdef class LegalMoves:
    cdef mpz_t*** moves             # 64 x 16 x variable
    cdef int** lens                 # 64 x 16
    cdef Check check
    cdef CastleMove castle_king
    cdef CastleMove castle_queen
    cdef mpz_t temp1
    cdef mpz_t temp2

    cdef mpz_t* child_states
    cdef int num_children

    cdef void expand_children_no_check(self, mpz_t state)
    cdef void expand_children(self, mpz_t state)
