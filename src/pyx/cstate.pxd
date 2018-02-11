#cython language_level=3

from gmpy2 cimport *

from gmp_funcs cimport *

# Represents a single possible board state
#   state           a bit vector representing the state
#   turn            turn number (1 means White's first move is about to happen)
#   value           valuation assigned to this state
#   quality         quality of the valuation
#   child           ID of the first child state
#   sibling         ID of the next child state which has the same parent as this state
#   num_children    number of children of this state (-2 if none, -1 if unknown)
cdef struct State:
    mpz_t state
    int turn
    int value
    int quality
    int child
    int sibling
    int num_children

cdef class StateList:
    cdef State* states
    cdef int num_states
    cdef int max_states
    cdef double resize_factor

    cdef next(self)
    cdef clear(self)

cdef class GameTree:
    cdef State* states
    cdef StateList statelist
    cdef mp_bitcnt_t bit_captured

    cdef next_state_id(self)
    cdef clear_states(self)
    cdef assign_children(self, int parent, mpz_t* children, int num_children)
    cdef add_state_c(self, mpz_t state, int turn)
