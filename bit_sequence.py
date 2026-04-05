'''Class BitSequence represents an iterable sequence of bits.'''


class BitSequence:
    '''Class representing a sequence of bits.'''

    _bits : list[int]  # list of bits in sequence (0/1 integers)

    def __init__(self) -> None:
        '''Create empty bit sequence.'''

        self._bits = []

    def append(self, bit: int) -> None:
        '''Append a single 0/1 bit to bit sequence.'''

        self._bits.append(bit)

    def extend(self, bits: list[int]) -> None:
        '''Append multiple bit:s to bit sequence.'''

        self._bits.extend(bits)

    def __iter__(self) -> BitIterator:
        '''Return iterator over the bits of the sequence.'''

        return BitIterator(self)

    def __repr__(self) -> str:
        '''Return string representation of bit sequence.'''

        return ''.join(map(str, self._bits))


class BitIterator:
    '''Iterator over a BitSequence.'''

    def __init__(self, bits: BitSequence) -> None:
        '''Initialize iterator over BitSequence bits.'''

        self._it = iter(bits._bits)

    def __next__(self) -> int:
        '''Return next bit in sequence.'''

        return next(self._it)

    def __iter__(self) -> BitIterator:
        '''Return self as iterator (making an iterator iterable).'''

        return self

    def get_integer(self, width: int) -> int:
        '''Return next width bits as integer (lsb first).'''

        return sum(next(self) << i for i in range(width))
