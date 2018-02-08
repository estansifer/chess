#cython language_level=3

from gmpy2 cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

from gmp_funcs cimport *

cdef class StateList:
    def __cinit__(self, int size, double resize):
        self.num_states = 0
        self.max_states = size
        self.resize_factor = resize
        self.states = <State *>PyMem_Malloc(size * sizeof(State))
        cdef int i
        for i in range(size):
            mpz_init2(self.states[i].state, 64 + 360)

    cdef next(self):
        cdef int new_max, i
        if self.num_states == self.max_states:
            new_max = int(self.max_states * self.resize_factor)
            new_states = <State *>PyMem_Realloc(self.states, new_max * sizeof(State))
            if not new_states:
                raise MemoryError()

            for i in range(self.max_states, new_max):
                mpz_init2(new_states[i].state, 64 + 360)

            self.states = new_states
            self.max_states = new_max

        self.num_states += 1
        return self.num_states - 1

    cdef clear(self):
        self.num_states = 0

    def __dealloc(self):
        cdef int i
        for i in range(self.max_states):
            mpz_clear(self.states[i].state)
        PyMem_Free(self.states)

cdef class GameTree:
    def __cinit__(self, StateList statelist, int bit_captured):
        self.statelist = statelist
        self.states = statelist.states
        self.bit_captured = bit_captured

    cdef next_state_id(self):
        cdef int i = self.statelist.next()

        # Initialize
        self.states[i].turn = -1
        self.states[i].value = 0
        self.states[i].quality = 0
        self.states[i].child = -1
        self.states[i].sibling = -1
        self.states[i].num_children = -1

        return i

    cdef clear_states(self):
        self.statelist.clear()

    cdef assign_children(self, int parent, mpz_t* children, int num_children):
        cdef int cur, n, i, turn
        self.states[parent].num_children = num_children
        if num_children == 0:
            self.states[parent].child = -2
        else:
            turn = self.states[parent].turn + 1

            n = self.next_state_id()
            self.states[parent].child = n
            mpz_set(self.states[n].state, children[0])
            self.states[n].turn = turn

            cur = n
            for i in range(1, num_children):
                n = self.next_state_id()
                mpz_set(self.states[n].state, children[i])
                self.states[n].turn = turn
                self.states[cur].sibling = n
                cur = n

    cdef add_state_c(self, mpz_t state, int turn):
        cdef int n = self.next_state_id()
        mpz_set(self.states[n].state, state)
        self.states[n].turn = turn

        return n

    def add_state(self, object state, int turn):
        return self.add_state_c(MPZ(state), turn)

    def find_state(self, object state, int turn):
        cdef int i
        for i in range(self.statelist.num_states):
            if (self.states[i].turn == turn) and (mpz_cmp(self.states[i].state, MPZ(state)) == 0):
                return i
        return -1

    def rebase_at(self, int root):
        mpz_set(self.states[0].state, self.states[root].state)
        self.states[0].turn = self.states[root].turn
        self.states[0].value = self.states[root].value
        self.states[0].quality = self.states[root].quality
        self.states[0].child = -1
        self.states[0].sibling = -1
        self.states[0].num_children = -1
        self.statelist.num_states = 1

    def turn(self, int n):
        return self.states[n].turn

    def child(self, int n):
        return self.states[n].child

    def sibling(self, int n):
        return self.states[n].sibling

    def value(self, int n):
        return self.states[n].value

    def set_value(self, int n, int value, int quality):
        self.states[n].value = value
        self.states[n].quality = quality

    def noisy(self, int n):
        return mpz_tstbit(self.states[n].state, self.bit_captured)

    def number_nodes(self):
        return self.statelist.num_states

    def __dealloc__(self):
        pass
