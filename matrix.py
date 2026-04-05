'''Class Matrix supports M[i, j] indexing and listing all cell indices.'''

type Cell = tuple[int, int]


class Matrix:
    '''Matrix supporting M[i, j] indexing.'''

    shape: Cell
    data: list[list[int]]

    def __init__(self, m: int | None = None, n: int | None = None,
                 data: list[list[int]] | None = None) -> None:

        '''Create m x n matrix filled with zeros, or matrix with given data.
        
        Matrix(m, n) creates an m x n matrix filled with zeros.
        Matrix(data=[[...],...,[...]]) creates a matrix with given data.        
        '''

        if data is not None:
            assert m is None and n is None
            m = len(data)
            n = len(data[0]) if data else 0
        else:
            assert m is not None and n is not None
            data = [[0] * n for _ in range(m)]
        self.shape = (m, n)
        self.data = data

    def __getitem__(self, key: Cell) -> int:
        '''M[i, j] returns entry (i, j) of the matrix.'''

        i, j = key
        return self.data[i][j]

    def __setitem__(self, key: Cell, value: int) -> None:
        '''M[i, j] = value : sets entry (i, j) of the matrix to value.'''

        i, j = key
        self.data[i][j] = value

    def cells(self) -> list[Cell]:
        '''Return a list of all cell indices (i, j) of the matrix.'''

        m, n = self.shape
        return [(i, j) for i in range(m) for j in range(n)]
