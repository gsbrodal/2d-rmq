'''Binary encoding and decoding functions for integers and trees.'''

from tree import Tree
from bit_sequence import BitSequence, BitIterator


def encode_unary(bits: BitSequence, value: int) -> None:
    '''Append to bit sequence unary encoding of positive integer.'''

    bits.extend([0] * (value - 1) + [1])


def encode_binary(bits: BitSequence, value: int, width: int) -> None:
    '''Append to bit sequence fixed width encoding of non-negative integer.'''

    bits.extend([(value >> i) & 1 for i in range(width)])


def decode_unary(bits: BitIterator) -> int:
    '''Decode from bit sequence unary integer.'''

    value = 1
    while next(bits) == 0:
        value += 1
    return value


def decode_binary(bits: BitIterator, width: int) -> int:
    '''Decode from bit sequence fixed width integer.'''

    return bits.get_integer(width)


def tree_encode(tree: Tree, bits: BitSequence, trim: bool = False) -> None:
    '''Append to bit sequence balanced parentheses encoding of tree.
    
    If trim=True, assumes tree contains at least two nodes, and skips from
    encoding the first two bits (both 1) and trailing 0 bits.
    '''

    nodes: int = 0

    def recursively_encode(node: Tree) -> None:
        nonlocal nodes
        nodes += 1
        if not trim or nodes >= 3:
            bits.append(1)
        for child in node.children:
            recursively_encode(child)
        if not trim or nodes < tree.size_nodes:
            bits.append(0)

    recursively_encode(tree)


def tree_decode(bits: BitIterator, size_nodes: int = -1, size_leaves: int = -1,
                trim: bool =  False) -> Tree:
    '''Decode tree from balanced parentheses encoding in bit sequence.
    
    If trim=True, requires tree to have at least two nodes. Assumes first two
    bits (both 1) and trailing 0 bits have been omitted from encoding.
    Trim=True requires either size_nodes or size_leaves to be provided.
    '''

    nodes: int = 0
    leaves: int = 0

    def recursively_decode() -> Tree:
        nonlocal nodes, leaves
        nodes += 1
        leaves += 1  # assume node is a leaf until we find out otherwise
        children: list[Tree] = []
        while (  # skip reading next bit for trailing 0s and if 2nd bit = 1
            not (trim and (leaves == size_leaves or nodes == size_nodes))
            and ((trim and nodes <= 1) or next(bits) == 1)
        ):
            if len(children) == 0:  # found first child, node not a leaf anyway
                leaves -= 1
            children.append(recursively_decode())

        return Tree(children)

    if not trim:
        next(bits)  # encoding starts with redundant 1, root opening
    return recursively_decode()
