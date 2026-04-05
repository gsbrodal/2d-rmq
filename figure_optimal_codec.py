'''Functions for generating TikZ figure of optimal codec.'''

import subprocess

from optimal_codec import State
from matrix import Matrix, Cell
from tree import Tree


def leaf_label(i: int) -> str:
    '''Labels for leaf nodes: L0, L1, ...'''

    return f'L{i}'


def internal_label(i: int) -> str:
    '''Labels for internal nodes: A, B, ..., Z, AA, AB, ...'''

    if i < 26:
        return chr(ord('A') + i)
    return internal_label(i // 26 - 1) + internal_label(i % 26)


def tree_layout(
        tree: Tree,
        position: dict[Tree, tuple[float, float]],
        label: dict[Tree, str], *,
        x: float = 0, y: float = 0,
        x_spacing: float = 1, y_spacing: float = 1
    ) -> float:
    '''Layout tree nodes in positions and label. Returns rightmost x.'''

    def recurse(tree: Tree, x: float, y: float) -> float:
        '''Layout tree. Top-left is (x, y). Returns rightmost x.'''

        if tree.children:
            label[tree] = internal_label(next(internal_labels))
            for child in tree.children:
                x = recurse(child, x, y - y_spacing) + x_spacing
            x -= x_spacing
            root_x = (position[tree.children[0]][0] +
                      position[tree.children[-1]][0]) / 2
            position[tree] = (root_x, y)
        else:
            label[tree] = leaf_label(next(leaf_labels))
            position[tree] = (x, y)
        return x

    leaf_labels = iter(range(tree.size_leaves))
    internal_labels = iter(range(tree.size_nodes - tree.size_leaves))
    return recurse(tree, x, y)


def tikz_decomposition_tree(
        tree: Tree,
        matrix: Matrix,
        cells: dict[Tree, Cell],
        label: dict[Tree, str],
        anchor_child: dict[Tree, int]
    ) -> str:
    '''TikZ figure of decomposition tree of matrix M.'''

    position: dict[Tree, tuple[float, float]] = {}
    tree_layout(tree, position, label)
    edges = [f'{label[u]}/{label[c]}'
             for u in tree.internal_nodes()
             for i, c in enumerate(u.children)
             if i != anchor_child[u]]
    anchor_edges = [f'{label[u]}/{label[c]}'
                    for u in tree.internal_nodes()
                    for i, c in enumerate(u.children)
                    if i == anchor_child[u]]
    internal_nodes = [f'{label[u]}/{position[u][0]}/{position[u][1]}/{{{label[u]}}}'
                      for u in tree.internal_nodes()]
    leaves = [f'{label[u]}/{position[u][0]}/{position[u][1]}/{{\\scriptsize({cells[u][0]},{cells[u][1]})}}\\\\{matrix[cells[u]]}'
              for u in tree.leaves()]

    return '\n'.join([
        r'\begin{tikzpicture}[thick, yscale=0.8, xscale=0.8, baseline=(T.south)]',
        r'  \node[anchor=north west](T) at (0,0) {$T$};',
        r'  \foreach \l/\x/\y/\t in { %s }' % ', '.join(internal_nodes),
        r'    \node[draw, circle, inner sep=2.5pt, outer sep=0pt,label=above:{\t}] (\l) at (\x,\y) {};',
        r'  \foreach \l/\x/\y/\t in { %s }' % ', '.join(leaves),
        r'    \node[draw, rectangle, outer sep=0pt,label=below:{\parbox{5em}{\centering \t}}] (\l) at (\x,\y) {};',
        r'  \foreach \u/\v in {' + ','.join(edges) + r'} \draw (\u)--(\v);',
        r'  \foreach \u/\v in {' + ','.join(anchor_edges) + r'}',
        r'    \draw[ultra thick, -latex] (\u)--(\v);',
        r'\end{tikzpicture}'
    ])


def parenthesis_tree(tree: Tree) -> str:
    '''Return balanced parentheses encoding of tree structure.'''

    return '(' + ''.join(parenthesis_tree(c) for c in tree.children) + ')'


def tikz_dfs_traversal(
        dfs_tree: Tree,
        dfs2tree: dict[Tree, Tree],
        cells: dict[Tree, Cell],
        label: dict[Tree, str],
        anchor_child: dict[Tree, int],
        interrupts: dict[Tree, list[tuple[int, int, int, int]]]
    ) -> str:
    '''TikZ figure of DFS traversal tree.'''

    pos: dict[Tree, tuple[float, float]] = {}
    dfs_label: dict[Tree, str] = {}
    x_right = tree_layout(dfs_tree, pos, dfs_label)

    name = {u: f"{label[dfs2tree[u]] if dfs2tree[u].children else f'{{\\scriptsize({cells[dfs2tree[u]][0]},{cells[dfs2tree[u]][1]})}}'}"
            for u in dfs_tree}

    nodes = [f'{label[dfs2tree[u]]}/{pos[u][0]}/{pos[u][1]}/{name[u]}'
             for u in dfs_tree]
    edges = [(v, child) for v in dfs_tree.internal_nodes()
             for child in v.children]
    child_edges = [f'{label[dfs2tree[u]]}/{label[dfs2tree[c]]}'
                   for u, c in edges
                   if dfs2tree[u].children]
    interrupt_edges = [f'{label[dfs2tree[u]]}/{label[dfs2tree[c]]}'
                       for u, c in edges
                       if not dfs2tree[u].children]

    return '\n'.join([
        r'\begin{tikzpicture}[thick, yscale=0.8, xscale=0.8, baseline=(base.south)]',
        r'  \node[anchor=north west](base) at (0,0) {dfs($T$)};',
        r'  \foreach \l/\x/\y/\t in { %s }' % ', '.join(nodes),
        r'    \node[inner sep=1pt] (\l) at (\x,\y) {\t};',
        r'  \foreach \u/\v in {' + ','.join(child_edges) + r'} \draw (\u)--(\v);',
        r'  \foreach \u/\v in {' + ','.join(interrupt_edges) + r'} \draw[dashed] (\u)--(\v);',
        r'  \foreach \u/\idx/\interrupts [count=\i from 1] in { %s } {' %
               ', '.join(f'{name[u]}/{anchor_child[dfs2tree[u]]}/{{{" ".join("(" + ",".join(map(str, i)) + ")" for i in interrupts[dfs2tree[u]])}}}' 
                         for u in dfs_tree if dfs2tree[u].children),
        r'    \node at (' + str(x_right + 2) + r', -\i*0.6) {\u};',
        r'    \node at (' + str(x_right + 3) + r', -\i*0.6) {\idx};',
        r'    \node[right] at (' + str(x_right + 4) + r', -\i*0.6) {\interrupts};',
        r'  }',
        r'\end{tikzpicture}'
    ])


def tikz_matrix(matrix: Matrix, tree: Tree, cells: dict[Tree, Cell]) -> str:
    '''TikZ figure of matrix M, optionally with decoded matrix M'.'''

    m, n = matrix.shape

    tex = [
        r'\begin{tikzpicture}[thick, yscale=0.5, xscale=0.9, baseline=(M.south)]',
        r'  \node[anchor=north](M) at ' f'({n/2},{-m})' ' {Input matrix $M$};',
        r'  \draw[line cap=rect] (0,0) grid (%s,-%s);' % (n, m),
        r'  \foreach \j in {0,...,' + str(n-1) + r'} \node[anchor=south] at (\j+0.5,0) {\scriptsize $\j$};',
        r'  \foreach \i in {0,...,' + str(m-1) + r'} \node[anchor=east] at (0,-\i-0.5) {\scriptsize $\i$};',
        r'  \foreach \row [count=\i from 0] in {', 
        ',\n'.join('    {' + ', '.join(map(str, row)) + '}' for row in matrix.data) + '}',
        r'  {',
        r'    \foreach \value [count=\j from 0] in \row {',
        r'      \node at (\j+0.5,-\i-0.5) {\value};',
        r'    }', 
        r'  }',
    ]
    if tree:
        tex += [
            r'  \begin{scope}[yshift=%s' 'cm]' % (-m - 1.5),
            r'    \foreach \i/\j [count=\k from 1] in {' + ','.join(f'{cells[u][0]}/{cells[u][1]}' for u in reversed(tree.leaves())) + '}',
            r'      \node at (\j+0.5,-\i-0.5) {\k};',
            r'    \draw[line cap=rect] (0,0) grid ++(%s,-%s);' % (n, m), 
            r'    \node[anchor=north] at ' f'({n/2},{-m})' r" {Decoded matrix $M'$};",
            r'  \end{scope}',
        ]
    tex += [
        r'\end{tikzpicture}'
    ]

    return '\n'.join(tex)


def tikz_optimal_codec(
        matrix: Matrix,
        final_state: State,
        file: str | None = None,
        pdflatex: bool = False
    ) -> str:
    '''TikZ figure for optimal codec applied to matrix M.'''

    (
        tree,
        cells,
        encoding,
        dfs_traversal,
        dfs_events,
        dfs2tree,
        anchor_child,
        interrupts
    ) = final_state

    tree_labels: dict[Tree, str] = {}

    tex = '\n'.join([
        r'\documentclass{standalone}',
        r'\usepackage{tikz}',
        r'\begin{document}',
        tikz_matrix(matrix, tree, cells) + '\n',
        tikz_decomposition_tree(
            tree,
            matrix,
            cells,
            tree_labels,
            anchor_child
        ) + '\n',
        tikz_dfs_traversal(
            dfs_traversal,
            dfs2tree,
            cells,
            tree_labels,
            anchor_child,
            interrupts
        ) + '\n',
        f'DFS events: {" ".join(map(str, dfs_events))}\n',
        f'Encoding: {encoding}\n\n' +
        r'\end{document}'
    ])

    if file:
        print(f'Saving LaTeX output to {file}')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(tex)
        if pdflatex:
            subprocess.run(
                f'pdflatex -interaction=nonstopmode {file}',
                check=True
            )

    return tex
