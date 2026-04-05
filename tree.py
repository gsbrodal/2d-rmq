'''Static tree class supporting navigation and rank information.'''

from typing import Iterator, Self


class Tree:
    '''Class representing a static tree.'''

    # Data attributes (type hints)
    children: list[Self]  # list of children, uses Self to support subclasses
    parent: Self          # parent of node, or self if node is root
    size_nodes: int       # number of nodes in subtree rooted at node
    size_leaves: int      # number of leaves in subtree rooted at node
    rank: int             # global rank of leftmost leaf in subtree

    def __init__(self, children: list[Self] | None = None) -> None:
        '''Create a node with the given children and additional attributes.'''

        if children is None:
            children = []
        self.parent = self
        self.children = children
        for child in children:
            child.parent = self
        self.size_nodes = 1 + sum(child.size_nodes for child in children)
        if children:
            self.size_leaves = sum(child.size_leaves for child in children)
        else:
            self.size_leaves = 1
        self.rank = 0  # global rank of leftmost leaf (set by annotate_ranks)

    def preorder(self) -> list[Self]:
        '''Return a list of all nodes in tree in preorder.'''

        def traverse(node: Self) -> None:
            nodes.append(node)
            for child in node.children:
                traverse(child)

        nodes: list[Self] = []
        traverse(self)
        return nodes

    def __iter__(self) -> Iterator[Self]:
        '''Iterate over all nodes in tree in preorder.'''

        return iter(self.preorder())

    def leaves(self) -> list[Self]:
        '''Return all leaves of tree left-to-right.'''

        return [node for node in self if not node.children]

    def internal_nodes(self) -> list[Self]:
        '''Return all internal nodes of tree in preorder.'''

        return [node for node in self if node.children]

    def annotate_ranks(self, rank: int = 0) -> None:
        '''Annotate tree with global rank of leftmost leaf in each subtree.'''

        self.rank = rank
        for child in self.children:
            child.annotate_ranks(rank)
            rank += child.size_leaves
