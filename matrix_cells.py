'''Maintain a monotonic decreasing set of indices into an m x n matrix.

Cells can be deleted in worst-case O(1) time. The L-neighbors of a cell can be
found in worst-case O(m) time, i.e., given a non-deleted cell c, all cells c'
are reported, where the only non-deleted cells in the rectangle Rect(c, c') are
c and c'.
'''

from interval_union_find import IntervalUnionFind
from matrix import Cell


class MonotonicMatrixCells:
    '''Maintain a monotonic decreasing set of indices into an m x n matrix.'''

    m: int
    n: int
    rows: list[IntervalUnionFind]

    def __init__(self, m: int, n: int) -> None:
        '''Init set to contain all cells of an m x n matrix.'''

        self.m = m
        self.n = n
        self.rows = [IntervalUnionFind(n) for _ in range(m)]

    def delete(self, cell: Cell) -> None:
        '''Remove cell from the set.'''

        i, j = cell
        self.rows[i].delete(j)

    def l_neighbor(self, cell: Cell, left_right: int, row: int) -> Cell:
        '''First non-deleted cell in row to the left/right (0/1) of cell.'''

        i, j = cell
        #assert j in self.rows[i]
        if left_right:  # strictly right of column j
            column = self.rows[row].successor(j + 1)
        else:  # left of column j (or equal to column j)
            column = self.rows[row].predecessor(j if i != row else j - 1)
        return (row, column)

    def l_neighbors(self, cell: Cell) -> list[Cell]:
        '''Cells c where only cell and c are not deleted in Rect[cell, c].'''

        i, j = cell
        assert j in self.rows[i]
        neighbors: list[Cell] = []
        left = self.rows[i].predecessor(j - 1)
        right = self.rows[i].successor(j + 1)
        if left >= 0:
            neighbors.append((i, left))
        if right < self.n:
            neighbors.append((i, right))
        for rows in (range(i - 1, -1, -1), range(i + 1, self.m)):
            l, r = left, right
            for i in rows:
                l_ = self.rows[i].predecessor(j)
                r_ = self.rows[i].successor(j)
                if l < l_:
                    l = l_
                    neighbors.append((i, l))
                if r_ < r:
                    r = r_
                    if l < r:  # don't include cell twice in output
                        neighbors.append((i, r))
        return neighbors
