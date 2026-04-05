'''Codec for suboptimal matrix encoding and decoding.

Size of encoding O(m * n * (log m + (log(m * n)) / alpha + log alpha)) bits.
'''

from matrix import Matrix, Cell
from bit_sequence import BitSequence, BitIterator
from tree import Tree
from matrix_codec import MatrixCodec
from matrix_cells import MonotonicMatrixCells
from encoding_utils import encode_unary, decode_unary, encode_binary, \
                           decode_binary, tree_encode, tree_decode


class SuboptimalCodec(MatrixCodec):
    '''Codec for suboptimal matrix encoding and decoding.

    Size of encoding O(m * n * (log m + (log(m * n)) / alpha + log alpha)) bits.
    '''

    alpha: int  # component size threshold
    trim: bool  # whether to remove redundant bits from encoding

    def __init__(self, alpha: int, trim: bool = False) -> None:
        '''Init codec with component threshold alpha and optimal trimming.'''

        self.alpha = alpha
        self.trim = trim

    def encode(self, matrix: Matrix) -> BitSequence:
        '''Encode matrix M as a bit sequence.'''

        def dfs(cell: Cell, parent_cell: Cell | None = None) -> Tree:
            '''Construct spanning tree of cells reachable from cell.'''

            visited.add(cell)
            edges.append((cell, parent_cell))
            nbs = L.l_neighbors(cell)
            # following sort is optional, only to be consistent with Fig. 1
            nbs.sort(key=lambda cell: matrix[cell], reverse=True)
            children = [dfs(child_cell, cell) for child_cell in nbs
                        if child_cell not in visited and child_cell in S]
            return Tree(children)

        m, n = matrix.shape
        m_length = m.bit_length()
        n_length = n.bit_length()

        # Global sort all matrix cells
        sorted_cells = sorted(matrix.cells(), key=lambda cell: matrix[cell])

        # Decompose m x n matrix into components with size threshold alpha
        components : list[list[Cell]] = []
        component_ids = Matrix(m, n)
        edge_labels: list[Cell] = []  # (left=0/right=1, row) pairs
        L: MonotonicMatrixCells = MonotonicMatrixCells(m, n)  # M cells not yet in a component
        S: set[Cell] = set()  # large value cells candidate for next component
        subtrees: list[Tree] = []
        for cell in reversed(sorted_cells):  # cells in decreasing value order
            S.add(cell)
            visited: set[Cell] = set()
            edges: list[tuple[Cell, Cell | None]] = []
            subtree = dfs(cell)  # dfs tree for cells reachable from cell
            if subtree.size_nodes >= self.alpha or cell == sorted_cells[0]:
                # Found next component (possibly by reaching last cell)
                subtrees.append(subtree)
                for cell, parent_cell in edges:
                    L.delete(cell)
                    component_ids[cell] = len(components)
                    if parent_cell is not None:  # edge label for non-root cells
                        i, j = cell
                        _, j_parent = parent_cell
                        edge_labels.append((int(j > j_parent), i))
                components.append([cell for cell, parent_cell in edges])
        tree = Tree(subtrees)

        anchor_cells = [component[0] for component in components]

        # Compute local ranks of cells in components
        next_local_rank = [0] * len(components)
        local_rank = Matrix(m, n)
        for cell in sorted_cells:
            component_id = component_ids[cell]
            local_rank[cell] = next_local_rank[component_id]
            next_local_rank[component_id] += 1
        local_ranks = []
        for component in components:
            cells = component[1:]
            if len(cells) >= 2:
                width = (len(cells) - 1).bit_length()  # local rank bit-length
                if self.trim:
                    cells.pop()  # Last local rank is redundant
                for cell in cells:
                    local_ranks.append((local_rank[cell] - 1, width))

        # Generate encoding
        bits = BitSequence()
        encode_unary(bits, m_length)
        encode_binary(bits, m, m_length)
        encode_unary(bits, n_length)
        encode_binary(bits, n, n_length)
        tree_encode(tree, bits, trim=self.trim)
        for i, j in anchor_cells:
            encode_binary(bits, i * n + j, (m * n - 1).bit_length())
        for left_right, i in edge_labels:
            bits.append(left_right)
            encode_binary(bits, i, (m - 1).bit_length())
        for rank, width in local_ranks:
            encode_binary(bits, rank, width)

        return bits


    def decode(self, bits: BitSequence) -> Matrix:
        '''Decode matrix from bit sequence.'''

        def decode_component(cell: Cell, root: Tree) -> None:
            '''Decode dfs events into component cells given root cell.'''

            component.append(cell)
            for child in root.children:
                left_right = next(bits_iter)
                i = decode_binary(bits_iter, (m - 1).bit_length())
                child_cell = L.l_neighbor(cell, left_right, i)
                decode_component(child_cell, child)

        bits_iter: BitIterator = iter(bits)
        m_bit_length = decode_unary(bits_iter)
        m = decode_binary(bits_iter, m_bit_length)
        n_bit_length = decode_unary(bits_iter)
        n = decode_binary(bits_iter, n_bit_length)
        root = tree_decode(bits_iter, size_nodes=m * n + 1, trim=self.trim)

        L = MonotonicMatrixCells(m, n)
        anchor_cells: list[Cell] = []
        components : list[list[Cell]] = []
        for subtree in root.children:
            anchor_idx = decode_binary(bits_iter, (m * n - 1).bit_length())
            anchor_cells.append((anchor_idx // n, anchor_idx % n))
        for anchor_cell, subtree in zip(anchor_cells, root.children):
            component: list[Cell] = []
            decode_component(anchor_cell, subtree)
            components.append(component)
            for cell in component:
                L.delete(cell)
        values = iter(range(m * n, 0, - 1))
        matrix = Matrix(m, n)
        for anchor_cell, component in zip(anchor_cells, components):
            size = len(component)
            if size <= 2:
                increasing = component
            else:
                width = (size - 2).bit_length()
                increasing = component[:1] + [component[-1]] * (size - 1)
                for cell in component[1:]:  # skip component root
                    if self.trim and cell == component[-1]:
                        continue
                    rank = 1 + decode_binary(bits_iter, width)
                    increasing[rank] = cell
            for cell in reversed(increasing):
                matrix[cell] = next(values)

        assert next(bits_iter, None) is None  # all bits should be consumed

        return matrix
