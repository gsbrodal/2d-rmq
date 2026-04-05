'''Abstract class MatrixCodec for matrix encoding and decoding schemes.'''

from matrix import Matrix
from bit_sequence import BitSequence


class MatrixCodec:
    '''Abstract class for matrix encoding and decoding schemes.'''

    def __init__(self) -> None:
        '''Create an instance of the codec (optionally with parameters).'''

        raise NotImplementedError

    def encode(self, matrix: Matrix) -> BitSequence:
        '''Encode matrix as a bit sequence.'''

        raise NotImplementedError

    def decode(self, bits: BitSequence) -> Matrix:
        '''Decode matrix from bit sequence.'''

        raise NotImplementedError
