'''Class implementing an interval union-find data structure.

The data structure maintains a set of integers from {0, 1, ..., n-1} under
deletions and successor/predecessor queries.

The data structure is essentially the two level "set-splitting" data
structure described in

    Harold N. Gabow, Robert Endre Tarjan:
    A Linear-Time Algorithm for a Special Case of Disjoint Set Union. 
    Journal of Computing and System Sciences, 30(2): 209-221 (1985)

supporting deletions in O(1) amortized time and predecessor and successor 
queries in worst-case O(1) time, assuming word_size >= log n.
'''


from word_functions import get_bit, clear_bit, msb_bit, lsb_bit, \
                           predecessor_bit, successor_bit


class IntervalUnionFind:
    '''Maintain {0,...,n-1} under deletions and successor/predecessor queries.

    Initialization takes O(n / word_size) time and space, queries O(1) time, and 
    deletions amortized O(1) time, assuming word_size >= log n.
    '''

    #  Example: Bit sequence partitioned into microsets for word_size = 5
    #
    #  Index w:          0       1       2       3       4       5
    #  Position:       01234   56789   ...                        n-1
    #  .micro-set[w]   00001 | 00000 | 01100 | 00000 | 00000 | 10101
    #  .macro_set[w]   [0,1]   [1,2]   [2,5]   [2,5]   [2,5]   [5,6]
    #  .macro_set[w]  = [i, j] where
    #     1) i <= w < j
    #     2) microsets i+1, ..., j-1 are all zero
    #     3) i = 0 or microset i-1 contains at least one
    #     4) j = ceil(n/word_size) or microset j contains at least one

    def __init__(self, n: int, word_size: int = 32) -> None:
        '''Initialize set to {0, 1, ..., n-1}.'''

        self._n = n
        self._word_size = word_size
        self._micro_sets = [(1 << min(word_size, n - i)) - 1
                            for i in range(0, n, word_size)]
        self._macro_sets = [[i, i + 1] for i in range(len(self._micro_sets))]

    def __contains__(self, i: int) -> bool:
        '''Return whether i is in the set.'''

        word_size = self._word_size
        return get_bit(self._micro_sets[i // word_size], i % word_size) == 1

    def successor(self, i: int) -> int:
        '''Return the smallest element >= i in the set, or n.'''

        if i >= self._n:
            return self._n                    # allow i >= n, return n
        i = max(i, 0)                         # allow i < 0, return successor(0)

        word_size = self._word_size
        w = i // word_size
        j = successor_bit(self._micro_sets[w], i % word_size)
        if j < 0:                         # Answer not in microset
            w = self._macro_sets[w][1]        # Next non-empty microset
            if w >= len(self._micro_sets):    # No such microset
                return self._n
            j = lsb_bit(self._micro_sets[w])  # Smallest index in microset
        return w * word_size + j

    def predecessor(self, i: int) -> int:
        '''Return the largest element <= i in the set, or -1.'''

        if i < 0:
            return -1                 # allow i < 0, returns -1
        i = min(i, self._n - 1)       # allow i >= n, returns predecessor(n - 1)

        word_size = self._word_size
        w = i // word_size
        j = predecessor_bit(self._micro_sets[w], i % word_size)
        if j < 0:                         # Answer not in microset
            if w == 0:                        # No previous microset
                return -1
            w = self._macro_sets[w - 1][0]    # First microset in interval left
            j = msb_bit(self._micro_sets[w])  # Largest index in microset
            if j < 0:                     # If no predecessor, return -1
                return -1
        return w * word_size + j

    def delete(self, i: int) -> None:
        '''Remove i from the set.'''

        word_size = self._word_size
        w = i // word_size
        b = i % word_size
        micro_set = self._micro_sets[w]
        if not get_bit(micro_set, b):  # i already deleted
            return
        micro_set = clear_bit(micro_set, b)
        self._micro_sets[w] = micro_set
        if micro_set != 0 or w == 0:  # No change to macrosets needed
            return
        # Merge this and the previous macrosets, by updating the smaller one
        ms1, ms2 = self._macro_sets[w - 1:w + 1]
        l1, r1 = ms1
        l2, r2 = ms2
        size1 = r1 - l1
        size2 = r2 - l2
        if size1 >= size2:
            ms1[1] = r2
            self._macro_sets[l2:r2] = [ms1] * size2
        else:
            ms2[0] = l1
            self._macro_sets[l1:r1] = [ms2] * size1
