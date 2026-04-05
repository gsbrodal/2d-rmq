'''Perform stress tests on matrix range minimum query (RMQ) encodings.

Performs tests on both the suboptimal O(mn*log m*loglog n) bit encoding and
optimal O(mn*log m) bit encoding, with and without trimming of redundant bits. 

Also creates TikZ figures for optimal encoding of matrices, which can be
compiled with pdflatex to create PDF figures illustrating the optimal encoding.
'''

import random
from matrix import Matrix
from test_rmq import test_matrix, test_stress, random_matrix
from optimal_codec import OptimalCodec
from suboptimal_codec import SuboptimalCodec
from figure_optimal_codec import tikz_optimal_codec

FIGURE_FILE = 'figure_optimal_codec.tex'

# Generate figure for optimal encoding
def figure_optimal_codec(matrix: Matrix) -> None:
    '''Create .tex figure with raw TikZ for optimal encoding of M.'''

    codec = OptimalCodec()
    test_matrix(matrix, codec)
    tikz_optimal_codec(
        matrix,
        codec.final_state,
        file=FIGURE_FILE,
        pdflatex=pdflatex
    )

# Matrix from Figure 3 in the paper
matrix_figure3 = Matrix(data=[
    [12, 4, 9, 18, 11, 14],
    [16, 8, 3, 10,  6,  1],
    [17, 5, 7, 15,  2, 13]
])

# Test encoding and decoding of M with different codecs and trim options
test_matrix(matrix_figure3, SuboptimalCodec(alpha=3, trim=False))
test_matrix(matrix_figure3, SuboptimalCodec(alpha=3, trim=True))
test_matrix(matrix_figure3, OptimalCodec(trim=False))
test_matrix(matrix_figure3, OptimalCodec(trim=True))

# Create figures for optimal encoding of random matrices
if input(f'Create latex figures ({FIGURE_FILE})? (y/N): ') == 'y':
    pdflatex = input('Run pdf_latex? (y/N): ') == 'y'
    figure_optimal_codec(matrix_figure3)
    while True:
        if input('Another figure? (y/N): ') != 'y':
            break
        figure_optimal_codec(random_matrix(3, 6))

# Stress test different codecs with different parameters
print('Performing stress tests (infinite loop)')
while True:
    for trim in (False, True):
        alpha = random.randint(1, 12)
        print(f'{trim=} {alpha=}')
        test_stress(SuboptimalCodec(alpha=alpha, trim=trim), tests=50)
        test_stress(OptimalCodec(trim=trim), tests=50)
