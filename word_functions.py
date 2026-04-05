'''Bit manipulation functions on integers/words of bits.'''


def get_bit(word: int, i: int) -> int:
    '''Return the i-th bit of word.'''

    return (word >> i) & 1

def set_bit(word: int, i: int) -> int:
    '''Return word with the i-th bit of word set.'''

    return word | (1 << i)

def clear_bit(word: int, i: int) -> int:
    '''Return word with the i-th bit of word cleared.'''

    return word & ~(1 << i)

def msb_bit(word: int) -> int:
    '''Return the index of the most significant bit of word, or -1.'''

    return word.bit_length() - 1 if word else -1

def lsb_bit(word: int) -> int:
    '''Return the index of the least significant bit of word, or -1.'''

    return msb_bit(word ^ (word - 1)) if word else -1

def predecessor_bit(word: int, i: int) -> int:
    '''Return the index of the most significant bit of word <= i, or -1.'''

    mask = (1 << i + 1) - 1
    return msb_bit(word & mask)

def successor_bit(word: int, i: int) -> int:
    '''Return the index of the least significant bit of word >= i, or -1.'''

    mask = (1 << i) - 1
    return lsb_bit(word & ~mask)
