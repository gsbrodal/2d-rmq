'''Optimal matrix encoding and decoding of size O(m * n * log m) bits.'''

from collections import defaultdict
from matrix_codec import MatrixCodec
from matrix import Matrix, Cell
from matrix_cells import MonotonicMatrixCells
from bit_sequence import BitSequence, BitIterator
from tree import Tree
from encoding_utils import encode_unary, decode_unary, encode_binary, \
    decode_binary, tree_encode, tree_decode
from connected_components import connected_components

type Interrupt = tuple[int, int, int, int] # (child_idx,local_rank,left_right,i)

type State = tuple[
    Tree,  # tree
    dict[Tree, Cell],  # node2cell
    BitSequence,  # encoding
    Tree,  # dfs_traversal
    list[int],  # dfs_events
    dict[Tree, Tree],  # dfs2tree
    dict[Tree, int],  # anchor_child
    dict[Tree, list[Interrupt]]  # interrupts
]

class OptimalCodec(MatrixCodec):
    '''Codec for matrix encoding and decoding of size O(m * n * log m) bits.'''

    final_state: State  # state after last encoding

    def __init__(self, trim: bool = False) -> None:
        '''Init codec with possible trimming of redundant bits.'''

        self.trim = trim

    def encode(self, matrix: Matrix) -> BitSequence:
        '''Encode matrix M as a bit sequence.'''

        def l_adj(c1: Cell, c2: Cell, L: set[Cell]) -> bool:
            '''L-adjacent query = rectangle[c1, c2] - {c1,c2} all in L.'''

            i1, j1 = c1
            i2, j2 = c2
            for i in range(min(i1, i2), max(i1, i2) + 1):
                for j in range(min(j1, j2), max(j1, j2) + 1):
                    c = (i, j)
                    if c not in L and c not in {c1, c2}:
                        return False
            return True

        def l_connected_components(C: set[Cell], L: set[Cell]) -> list[list[Cell]]:
            '''Find L-connected components in graph with cells C.'''

            adj: dict[Cell, list[Cell]] = {v: [] for v in C}
            for u in C:
                for v in C:
                    if u != v and l_adj(u, v, L):
                        adj[u].append(v)
            return connected_components(list(C), adj)

        def l_neighbors(cell: Cell) -> list[Cell]:
            '''Return cells in M that are L-adjacent to c.'''

            # m, n and L are non-local variables

            _, j = cell
            neighbors = []
            for i_ in range(m):
                for j_ in range(j - 1, -1, -1):  # left side
                    cell_ = (i_, j_)
                    if cell_ in L:
                        continue
                    if l_adj(cell, cell_, L):
                        neighbors.append(cell_)
                    break
                for j_ in range(j, n):  # right side
                    cell_ = (i_, j_)
                    if cell_ == cell or cell_ in L:
                        continue
                    if l_adj(cell, cell_, L):
                        neighbors.append(cell_)
                    break
            return neighbors

        def decompose(C: set[Cell]) -> Tree:
            '''Hierarchical decomposition (component size O(m * alpha)).'''

            assert len(l_connected_components(C, L)) == 1

            size = len(C)
            if size == 1:  # base case, single cell
                cell, = C
                L.add(cell)
                leaf = Tree()
                node2cell[leaf] = cell
                return leaf
            alpha = int(size ** 0.5)
            children: list[Tree] = []
            C = C.copy()  # C minus constructed children components
            S = set()  # candidate cells for next component, S <= C
            decreasing = sorted(C, key=lambda cell: matrix[cell], reverse=True)
            for cell in decreasing:  # consider cells in decreasing value order
                if cell in C and cell not in S:  # cell not yet in any component or S
                    S.add(cell)
                    for U in l_connected_components(C - S, L | S):
                        if len(U) < alpha:
#                           print(f'*** small component {U=} {alpha=} {S=} {C_=}')
                            S.update(U)
                    # Created MyPy issue: github.com/python/mypy/issues/21104
                    temp = max(l_connected_components(S, L), key=len)
                    X: set[Cell] = set(temp)
                    if len(X) == size:  # Only one component, children=leaves
                        return Tree([decompose({cell}) for cell in decreasing])
                    if len(X) >= alpha:  # new component X, recursion adds X to L
                        children.append(decompose(X))
                        C -= X
                        S -= X
                assert S <= C
                assert all(len(U) >= alpha for U in l_connected_components(C - S, L | S))
                assert all(len(U) < alpha for U in l_connected_components(S, L))
                assert all(matrix[s] >= matrix[c] for s in S for c in C - S if l_adj(s, c, L))
            assert len(S) == 0
            return Tree(children)

        def find_child(node: Tree, leaf: Tree) -> int:
            '''Find child index of node containing leaf with rank.'''

            for i, child in enumerate(node.children):
                if child.rank <= leaf.rank < child.rank + child.size_leaves:
                    return i
            raise ValueError

        def find_interrupts(node: Tree, anchor_leaf: Tree) -> Tree:
            '''Annotate nodes with interrupts from a dfs traversal of tree.'''

            dfs_children = []
            if node != anchor_leaf:  # internal node
                anchor_child[node] = find_child(node, anchor_leaf)
                dfs_child = find_interrupts(node.children[anchor_child[node]], anchor_leaf)
                dfs_children.append(dfs_child)
                while visible_neighbors[node]:
                    (u, v) = visible_neighbors[node].pop()
                    if node2cell[v] in L:
                        continue   # already visited v
                    child_idx = find_child(node, v)
                    local_rank = u.rank - node.rank
                    _, uj = node2cell[u]
                    i, vj = node2cell[v]
                    left_right = 0 if vj <= uj else 1
                    interrupts[node].append((child_idx, local_rank, left_right, i))
                    dfs_child = find_interrupts(node.children[child_idx], v)
                    dfs_children.append(dfs_child)
            else:  # leaf
                L.add(node2cell[anchor_leaf])
                while True:
                    # recurse on unprocessed L-neighbors to the left
                    nbs = [leaves[cell] for cell in l_neighbors(node2cell[anchor_leaf])]
                    left_nbs = [nb for nb in nbs if nb.rank < anchor_leaf.rank]
                    if not left_nbs:
                        break
                    # Process one left child of anchor_leaf
                    target = left_nbs.pop()
                    interrupt_height = 0
                    ancestor = node
                    while not ancestor.rank <= target.rank:
                        ancestor = ancestor.parent
                        interrupt_height += 1
                    child_idx = find_child(ancestor, target)
                    local_rank = anchor_leaf.rank - ancestor.rank
                    _, j1 = node2cell[anchor_leaf]
                    i, j2 = node2cell[target]
                    left_right = 0 if j2 <= j1 else 1
                    interrupts[ancestor].append((child_idx, local_rank, left_right, i))
                    dfs_events.append(interrupt_height)
                    dfs_child = find_interrupts(ancestor.children[child_idx], target)
                    dfs_children.append(dfs_child)
                for nb in nbs:  # add right neighbors to visible_neighbor lists
                    ancestor : Tree = node
                    while not nb.rank < ancestor.rank + ancestor.size_leaves:
                        ancestor = ancestor.parent
                    visible_neighbors[ancestor].append((anchor_leaf, nb))
                dfs_events.append(0)  # leaf interrupt
                node = anchor_leaf
            tree = Tree(dfs_children)
            dfs2tree[tree] = node
            return tree

        m, n = matrix.shape
        m_length = m.bit_length()
        n_length = n.bit_length()
        i_length = (m - 1).bit_length()
        node2cell: dict[Tree, Cell] = {}  # node2cell[tree_node] = matrix cell
        L: set[Cell] = set()  # cells in components constructed so far
        tree = decompose(set(matrix.cells()))
        tree.annotate_ranks()
        L = set()  # reset L for finding interrupts
        anchor_child: dict[Tree, int] = {}
        interrupts: dict[Tree, list[Interrupt]] = defaultdict(list)
        dfs_events: list[int] = []
        visible_neighbors: dict[Tree, list[tuple[Tree, Tree]]] = defaultdict(list)
        leaves = {node2cell[leaf]: leaf for leaf in tree.leaves()}
        dfs2tree: dict[Tree, Tree] = {}
        dfs_traversal = find_interrupts(tree, anchor_leaf=leaves[(0, 0)])

        bits = BitSequence()
        encode_unary(bits, m_length)
        encode_binary(bits, m, m_length)
        encode_unary(bits, n_length)
        encode_binary(bits, n, n_length)
        tree_encode(tree, bits, trim=self.trim)
        # Encode anchor children and interrupts
        for node in tree.internal_nodes():
            local_rank_length = (node.size_leaves - 1).bit_length()
            child_idx_length = (len(node.children) - 1).bit_length()
            if not self.trim:
                encode_binary(bits, anchor_child[node], child_idx_length)
            for child_idx, local_rank, left_right, i in interrupts[node]:
                encode_binary(bits, child_idx, child_idx_length)
                encode_binary(bits, local_rank, local_rank_length)
                encode_binary(bits, left_right, 1)
                encode_binary(bits, i, i_length)
        if self.trim:
            dfs_events.pop()  # remove last zero (return from last leaf)
        # Encode DFS events
        for interrupt_height in dfs_events:
            encode_unary(bits, interrupt_height + 1)

        # Save state for LaTeX figure generation
        self.final_state = (
            tree,
            node2cell,
            bits,
            dfs_traversal,
            dfs_events,
            dfs2tree,
            anchor_child,
            interrupts
        )

        return bits

    def decode(self, bits: BitSequence) -> Matrix:
        '''Decode matrix from bit sequence.'''

        def apply_interrupts(node: Tree, anchor_cell: Cell) -> None:
            '''Process all interrupts at node given anchor cell for subtree.'''

            if node.children:  # internal node, go to anchor child
                apply_interrupts(node.children[anchor_child[node]], anchor_cell)
                while interrupts[node]:
                    child_idx, local_rank, left_right, i = interrupts[node].pop()
                    child = node.children[child_idx]
                    cell = leaves[node.rank + local_rank]
                    neighbor = L.l_neighbor(cell, left_right, i)
                    apply_interrupts(child, neighbor)
            else:  # leaf node, interrupt to ancestor or return from leaf
                leaves[node.rank] = anchor_cell
                L.delete(anchor_cell)
                while (interrupt_height := dfs_events.pop()) > 0:
                    ancestor = node
                    for _ in range(interrupt_height):
                        ancestor = ancestor.parent
                    child_idx, local_rank, left_right, i = interrupts[ancestor].pop()
                    child = ancestor.children[child_idx]
                    cell = leaves[ancestor.rank + local_rank]
                    neighbor = L.l_neighbor(cell, left_right, i)
                    apply_interrupts(child, neighbor)

        bits_iter: BitIterator = iter(bits)
        m_length = decode_unary(bits_iter)
        m = decode_binary(bits_iter, m_length)
        n_length = decode_unary(bits_iter)
        n = decode_binary(bits_iter, n_length)
        tree = tree_decode(bits_iter, size_leaves=m * n, trim=self.trim)

        # Read anchor children and interrupts
        i_length = (m - 1).bit_length()
        anchor_child: dict[Tree, int] = {}
        interrupts: dict[Tree, list[Interrupt]] = defaultdict(list)
        for node in tree.internal_nodes():
            degree = len(node.children)
            child_idx_length = (degree - 1).bit_length()
            local_rank_length = (node.size_leaves - 1).bit_length()
            if not self.trim:
                anchor_child[node] = decode_binary(bits_iter, child_idx_length)
            for _ in range(degree - 1):  # read interrupts
                child_idx = decode_binary(bits_iter, child_idx_length)
                local_rank = decode_binary(bits_iter, local_rank_length)
                left_right = decode_binary(bits_iter, 1)
                i = decode_binary(bits_iter, i_length)
                interrupts[node].append((child_idx, local_rank, left_right, i))
            if self.trim:  # anchor child is only child with no interrupt
                child_idxs = {i for i, _, _, _ in interrupts[node]}
                anchor_child[node] = (set(range(degree)) - child_idxs).pop()
            interrupts[node].reverse()

        # Read DFS events
        dfs_events = []
        leaves_done = 0
        while leaves_done < m * n - self.trim:
            interrupt_height = decode_unary(bits_iter) - 1
            dfs_events.append(interrupt_height)
            if interrupt_height == 0:
                leaves_done += 1
        if self.trim:
            dfs_events.append(0)
        dfs_events.reverse()

        # Process DFS events and interrupts to find leaf cells
        leaves : list[Cell] = [(0, 0)] * (m * n)  # leaves[rank] = rank'th leaf
        L = MonotonicMatrixCells(m, n)
        tree.annotate_ranks()
        apply_interrupts(tree, anchor_cell=(0, 0))

        # Construct matrix M from right-to-left order of leaf cells
        matrix = Matrix(m, n)
        for i, cell in enumerate(reversed(leaves)):
            matrix[cell] = i

        assert next(bits_iter, None) is None  # all bits should be consumed

        return matrix
