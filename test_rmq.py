'''Functions to test integrity of 2D RMQ MatrixCodec (encoding and decoding).'''

import random
from matrix import Matrix, Cell
from matrix_codec import MatrixCodec


def rmq(matrix: Matrix, i1: int, j1: int, i2: int, j2: int) -> Cell:
    '''Find cell where M[cell] is minimum within range (i1, j1) to (i2, j2).'''

    cell = i1, j1
    for i in range(min(i1, i2), max(i1, i2) + 1):
        for j in range(min(j1, j2), max(j1, j2) + 1):
            if matrix[i, j] < matrix[cell]:
                cell = i, j
    return cell


def rmq_consistency(m1: Matrix, m2: Matrix) -> None:
    '''Test if all possible RMQ answers on M1 and M2 are consistent.'''

    assert m1.shape == m2.shape
    m, n = m1.shape
    for i1 in range(m):
        for j1 in range(n):
            for i2 in range(i1, m):
                for j2 in range(j1, n):
                    assert rmq(m1, i1, j1, i2, j2) == rmq(m2, i1, j1, i2, j2)


def test_matrix(matrix: Matrix, codec: MatrixCodec) -> None:
    '''Test encoding and decoding of matrix for consistent RMQ answers.'''

    bits = codec.encode(matrix)
    decoded_matrix = codec.decode(bits)
    rmq_consistency(matrix, decoded_matrix)


def random_matrix(m: int, n: int) -> Matrix:
    '''Return random m x n matrix with distinct values.'''

    values = list(range(1, 1 + m * n))
    random.shuffle(values)
    return Matrix(data=[values[i:i + n] for i in range(0, m * n, n)])


def test_stress(
        codec: MatrixCodec, *,
        tests: int = 100,
        min_m: int = 1,
        max_m: int = 10,
        min_n: int = 1,
        max_n: int = 20
    ) -> None:
    '''Stress test 2D RMQ encoding and decoding on random matrices.'''

    for test in range(1, tests + 1):
        # Use \r (carriage return) to overwrite previous line
        print(f'\r{type(codec).__name__} [{test} tests]', end='', flush=True)

        # Random input matrix M
        m = random.randint(min_m, max_m)
        n = random.randint(min_n, max_n)
        matrix = random_matrix(m, n)
        test_matrix(matrix, codec)
    print()
