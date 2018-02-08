#!python
#cython language_level=3

from gmpy2 cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Free

from gmp_funcs cimport *
from cstate cimport GameTree

# An instance of this class checks for whether a specific color king is in check
# (or is illegally capturable)
cdef class Check:
    def __cinit__(self, object mpzss, int bits_king, int bit_turn):
        self.indices = <int *>PyMem_Malloc(65 * sizeof(int))

        self.indices[0] = 0
        cdef int i
        for i in range(64):
            self.indices[i + 1] = self.indices[i] + 2 * len(mpzss[i])

        cdef int n = self.indices[64]

        self.captures_rev = <mpz_t *>PyMem_Malloc(n * sizeof(mpz_t))

        for i in range(64):
            for j in range(len(mpzss[i])):
                mpz_init_set(self.captures_rev[self.indices[i] + 2 * j], MPZ(mpzss[i][j][0]))
                mpz_init_set(self.captures_rev[self.indices[i] + 2 * j + 1], MPZ(mpzss[i][j][1]))

        mpz_init2(self.state, 64 + 360)
        mpz_init2(self.temp, 64 + 360)
        self.bits_king = bits_king
        self.bit_turn = bit_turn

    def set_state(self, GameTree tree, int n):
        mpz_set(self.state, tree.states[n].state)

    def illegal_check(self):
        return self.can_take_king() == 1

    def in_check(self):
        mpz_combit(self.state, self.bit_turn)
        return self.can_take_king() == 1

    cdef illegal_check_c(self, mpz_t state):
        mpz_set(self.state, state)
        return self.can_take_king()

    cdef in_check_c(self, mpz_t state):
        mpz_set(self.state, state)
        mpz_combit(self.state, self.bit_turn)
        return self.can_take_king()

    cdef can_take_king(self):
        mpz_fdiv_q_2exp(self.temp, self.state, self.bits_king)
        cdef mp_limb_t leastsig = mpz_getlimbn(self.temp, 0)
        cdef int king_square = <int>(leastsig & 0b111111)
        cdef int i
        for i in range(self.indices[king_square], self.indices[king_square + 1], 2):
            mpz_and(self.temp, self.state, self.captures_rev[i])
            if mpz_cmp(self.temp, self.captures_rev[i + 1]) == 0:
                return 1
        return 0

    def __dealloc__(self):
        cdef int i
        for i in range(self.indices[64]):
            mpz_clear(self.captures_rev[i])
        PyMem_Free(self.captures_rev)
        PyMem_Free(self.indices)
        mpz_clear(self.state)
        mpz_clear(self.temp)

# An instance of this class represents a specific possible move, and
# can check whether that move is legal in a specified position, including
# checking for going into an illegal check.
cdef class MoveNoCheck:
    def __cinit__(self, object move, object captures):
        mpz_init_set(self.check_mask, MPZ(move[0]))
        mpz_init_set(self.check_result, MPZ(move[1]))
        mpz_init_set(self.set_and, MPZ(move[2]))
        mpz_init_set(self.set_or, MPZ(move[3]))

        cdef int n = len(captures)
        self.num_captures = n
        self.captures = <mpz_t *>PyMem_Malloc(2 * n * sizeof(mpz_t))
        cdef int i
        for i in range(n):
            mpz_init_set(self.captures[2 * i], MPZ(captures[i][0]))
            mpz_init_set(self.captures[2 * i] + 1, MPZ(captures[i][1]))

        mpz_init2(self.result, 64 + 360)
        mpz_init2(self.temp, 64 + 360)

    # Returns 1 if the move is legal and does not go into check, 0 otherwise.
    # If the return value is 1, then the new state is in self.result.
    cdef int move(self, mpz_t state):
        mpz_and(self.temp, state, self.check_mask)
        if mpz_cmp(self.temp, self.check_result) != 0:
            return 0

        mpz_and(self.result, state, self.set_and)
        mpz_ior(self.result, self.result, self.set_or)

        cdef int i
        for i in range(self.num_captures):
            mpz_and(self.temp, self.result, self.captures[2 * i])
            if mpz_cmp(self.temp, self.captures[2 * i + 1]) == 0:
                return 0

        return 1

    def __dealloc__(self):
        PyMem_Free(self.captures)
        mpz_clear(self.check_mask)
        mpz_clear(self.check_result)
        mpz_clear(self.set_and)
        mpz_clear(self.set_or)
        mpz_clear(self.result)
        mpz_clear(self.temp)

# An instance of this class represents one of the four possible castling moves
cdef class CastleMove:
    def __cinit__(self, MoveNoCheck castle, MoveNoCheck move_int1, MoveNoCheck move_int2):
        self.castle = castle
        self.move_int1 = move_int1
        self.move_int2 = move_int2
        mpz_init2(self.result, 64 + 360)

    # Returns 1 if the castle move is legal and does not go into check, 0 otherwise.
    # If the return value is 1, then the new state is in self.result.
    cdef int move(self, mpz_t state):
        if self.move_int1.move(state) == 0:
            return 0
        if self.move_int2.move(state) == 0:
            return 0
        if self.castle.move(state) == 0:
            return 0
        mpz_set(self.result, self.castle.result)

        return 1

    def __dealloc__(self):
        mpz_clear(self.result)

# An instance of this class represents all possible legal moves of one color in chess,
# excluding castling moves.
cdef class LegalMoves:
    def __cinit__(self, object mpzsss, Check check, CastleMove ck, CastleMove cq):
        self.check = check
        self.castle_king = ck
        self.castle_queen = cq
        mpz_init2(self.temp1, 64 + 360)
        mpz_init2(self.temp2, 64 + 360)

        self.lens = <int **>PyMem_Malloc(64 * sizeof(int *))
        self.moves = <mpz_t ***>PyMem_Malloc(64 * sizeof(mpz_t **))
        cdef int i, j, k, l, n
        for i in range(64):
            self.lens[i] = <int *>PyMem_Malloc(16 * sizeof(int))
            self.moves[i] = <mpz_t **>PyMem_Malloc(16 * sizeof(mpz_t *))
            for j in range(16):
                n = len(mpzsss[i][j])
                self.lens[i][j] = n
                self.moves[i][j] = <mpz_t *>PyMem_Malloc(4 * n * sizeof(mpz_t))
                for k in range(n):
                    for l in range(4):
                        mpz_init_set(self.moves[i][j][4 * k + l], MPZ(mpzsss[i][j][k][l]))

        self.child_states = <mpz_t *>PyMem_Malloc(500 * sizeof(mpz_t))
        for i in range(500):
            mpz_init2(self.child_states[i], 64 + 360)
        self.num_children = 0

    # After this call is completed, self.child_states stores a list of child states
    # and self.num_children stores the number of child states.
    cdef void expand_children_no_check(self, mpz_t state):
        self.num_children = 0

        mpz_set(self.temp1, state)

        cdef int i, j, n, piece
        cdef mp_limb_t leastsig
        cdef mpz_t* mpzs
        for i in range(64):
            leastsig = mpz_getlimbn(self.temp1, 0)
            piece = <int>(leastsig & 0b1111)
            n = self.lens[i][piece]
            mpzs = self.moves[i][piece]

            for j in range(n):
                mpz_and(self.temp2, state, mpzs[4 * j])
                if mpz_cmp(self.temp2, mpzs[4 * j + 1]) == 0: # legal move
                    mpz_and(self.temp2, state, mpzs[4 * j + 2])
                    mpz_ior(self.child_states[self.num_children], self.temp2, mpzs[4 * j + 3])
                    self.num_children += 1

            mpz_fdiv_q_2exp(self.temp1, self.temp1, 5)

        if self.castle_king.move(state) == 1:
            mpz_set(self.child_states[self.num_children], self.castle_king.result)
            self.num_children += 1
        if self.castle_queen.move(state) == 1:
            mpz_set(self.child_states[self.num_children], self.castle_queen.result)
            self.num_children += 1

    # Same, but only includes child states that do not go into an illegal check
    cdef void expand_children(self, mpz_t state):
        self.num_children = 0

        mpz_set(self.temp1, state)

        cdef int i, j, n, piece
        cdef mp_limb_t leastsig
        cdef mpz_t* mpzs
        for i in range(64):
            leastsig = mpz_getlimbn(self.temp1, 0)
            piece = <int>(leastsig & 0b1111)
            n = self.lens[i][piece]
            mpzs = self.moves[i][piece]

            for j in range(n):
                mpz_and(self.temp2, state, mpzs[4 * j])
                if mpz_cmp(self.temp2, mpzs[4 * j + 1]) == 0: # legal move
                    mpz_and(self.temp2, state, mpzs[4 * j + 2])
                    mpz_ior(self.temp2, self.temp2, mpzs[4 * j + 3])
                    if self.check.illegal_check_c(self.temp2) == 0:
                        mpz_set(self.child_states[self.num_children], self.temp2)
                        self.num_children += 1

            mpz_fdiv_q_2exp(self.temp1, self.temp1, 5)

        if self.castle_king.move(state) == 1:
            mpz_set(self.child_states[self.num_children], self.castle_king.result)
            self.num_children += 1
        if self.castle_queen.move(state) == 1:
            mpz_set(self.child_states[self.num_children], self.castle_queen.result)
            self.num_children += 1

    def __dealloc__(self):
        cdef int i, j, k, l, n
        for i in range(64):
            for j in range(16):
                n = self.lens[i][j]
                for k in range(n):
                    for l in range(4):
                        mpz_clear(self.moves[i][j][4 * k + l])
                PyMem_Free(self.moves[i][j])
            PyMem_Free(self.lens[i])
            PyMem_Free(self.moves[i])
        PyMem_Free(self.lens)
        PyMem_Free(self.moves)
        mpz_clear(self.temp1)
        mpz_clear(self.temp2)

        for i in range(500):
            mpz_clear(self.child_states[i])
        PyMem_Free(self.child_states)

def add_children(GameTree tree, int parent, LegalMoves white, LegalMoves black):
    if tree.states[parent].num_children != -1:
        return

    cdef LegalMoves moves
    if tree.states[parent].turn & 1 == 0:
        moves = black
    else:
        moves = white

    moves.expand_children(tree.states[parent].state)
    tree.assign_children(parent, moves.child_states, moves.num_children)
