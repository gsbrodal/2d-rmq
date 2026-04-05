'''Create TikZ figure illustrating the partitioning of a matrix.'''

from collections import defaultdict
import subprocess
from matrix import Cell

TEXFILE = 'figure_partition.tex'

# Example of a partition: L and R are cells to the left and right of the current
# component under consideration, respectively, C|A|B|S the current component
# being partitioned. S = the part of "C" that has been moved to S, essentially
# large elements and adjacent components smaller than alpha. A and B are C cells
# to be emphasized in the figure (A = red, B later to become A).

MATRIX = '''
LCCRSRCC
LLCRSCLL
CLLLSCLS
CCCLLLLL
RRRLRRCC
RBBLRRCC
CSASCCCR
'''


def indent(tex: str, columns: int) -> str:
    '''Indent multiline tex by given number of spaces.'''

    return ''.join(' ' * columns + line + '\n' for line in tex.splitlines())


def tex_scope(tex: str, args: str) -> str:
    '''Enclose TikZ code in scope environment with given arguments.'''

    return '\\begin{scope}[%s]\n%s\\end{scope}\n' % (args, indent(tex, 2))


def tex_cells(cells: set[Cell]) -> str:
    '''Create TikZ list of matrix cells: i1/j1, ...'''

    return ', '.join(f'{i}/{j}' for i, j in cells)


def tex_edges(edges: set[tuple[Cell, Cell]]) -> str:
    '''Create TikZ list of matrix edges: i1/j1/i2/j2, ...'''

    return ', '.join(f'{i1}/{j1}/{i2}/{j2}' for (i1, j1), (i2, j2) in edges)


def l_adjacent(cell1: Cell, cell2: Cell, L: set[Cell]) -> bool:
    '''Check if cell1 and cell2 are L-adjacent.'''

    (i1, j1), (i2, j2) = cell1, cell2
    for i in range(min(i1, i2), max(i1, i2) + 1):
        for j in range(min(j1, j2), max(j1, j2) + 1):
            cell = (i, j)
            if not (cell in {cell1, cell2} or cell in L):
                return False
    return True


def l_edges(cells: set[Cell], L: set[Cell]) -> set[tuple[Cell, Cell]]:
    '''Find all L-edges between given cells.'''

    cells_inc = sorted(cells)
    return {(cell1, cell2)
            for i, cell1 in enumerate(cells_inc)
            for cell2 in cells_inc[i+1:]
            if l_adjacent(cell1, cell2, L)}


def partition_figure(
        matrix: str,
        label: str,
        edges_prev: set[tuple[Cell, Cell]] | None = None,
    ) -> tuple[str, set[tuple[Cell, Cell]]]:
    '''Create TikZ subfigure label.'''

    lines = matrix.strip().split()
    m = len(lines)
    n = len(lines[0])

    assert all(len(line) == n for line in lines)
    assert all(c in 'LRSCAB' for line in lines for c in line)

    cells_by = defaultdict(set)  # cells_by[char] = list((i, j))
    for i,  row in enumerate(lines):
        for j, c in enumerate(row):
            cells_by[c].add((i, j))

    L, C, S, A, B = map(cells_by.__getitem__, 'LCSAB')
    C = C | A | B
    edges_sc = {(s, c) for s in S for c in C - S if l_adjacent(s, c, L)}
    old_edges: set[tuple[Cell, Cell]] = l_edges(C - S, L) | l_edges(S, L)
    new_edges = set()
    if edges_prev is not None:
        new_edges = old_edges - edges_prev
        old_edges = old_edges & edges_prev

    return (
''. join(r'''\foreach \i/\j in {%s}
  \fill[%s] (\j,-\i) rectangle (\j+1,-\i-1);
''' % (tex_cells(cells), color)
    for cells, color in [
        (L, 'black!25'),
        (C - S, 'blue!20!red!20'),
        (S, 'blue!20')
    ]
    if cells
) +
r'''\node[anchor=north east] (0, 0) {''' + label + r''')};
\foreach \i/\j in {''' + tex_cells(A) + r'''}
  \draw[line width=2pt, color=red] (\j,-\i) rectangle (\j+1,-\i-1);
\foreach \i/\j/\k/\l in {''' + tex_edges(old_edges) + r'''}
  \draw[line width=2pt] (\j+0.5,-\i-0.5) -- (\l+0.5,-\k-0.5);
\foreach \i/\j/\k/\l in {''' + tex_edges(new_edges) + r'''}
  \draw[line width=2pt, dotted] (\j+0.5,-\i-0.5) -- (\l+0.5,-\k-0.5);
\foreach \i/\j/\k/\l in {''' + tex_edges(edges_sc) + r'''}
  \draw[dashed, line width=2pt] (\j+0.5,-\i-0.5) -- (\l+0.5,-\k-0.5);
\foreach \i/\j in {%s}
  \fill (\j+0.5,-\i-0.5) circle (0.1);
\draw(0,0) grid (%s,-%s);''' % (tex_cells(C | S), n, m)
    ), l_edges(C, L)

MATRIX2 = MATRIX.replace('S', 'L').replace('A', 'C')
MATRIX3 = MATRIX.replace('A', 'S')
MATRIX4 = MATRIX3.replace('S', 'L').replace('B', 'A')
MATRIX5 = MATRIX3.replace('B', 'S')
MATRIX6 = MATRIX5.replace('C', 'R')
MATRIX7 = MATRIX5[::-1].replace('S', 'L', count=5)[::-1]
MATRIX8 = MATRIX7.replace('S', 'L')
fig1_tex, edges1 = partition_figure(MATRIX, label='a')
fig2_tex, edges2 = partition_figure(MATRIX2, label='b', edges_prev=edges1)
fig3_tex, edges3 = partition_figure(MATRIX3, label='c')
fig4_tex, edges4 = partition_figure(MATRIX4, label='d', edges_prev=edges3)
fig5_tex, edges5 = partition_figure(MATRIX5, label='e')
fig6_tex, edges6 = partition_figure(MATRIX6, label='f')
fig7_tex, edges7 = partition_figure(MATRIX7, label='g')
fig8_tex, edges8 = partition_figure(MATRIX8, label='h', edges_prev=edges7)

TEX = (
r'''\documentclass{standalone}
\usepackage{tikz}
\begin{document}
\begin{tikzpicture}
''' +
indent(
  tex_scope(fig1_tex, 'xshift=0cm') +
  tex_scope(fig2_tex, 'xshift=10cm') +
  tex_scope(fig3_tex, 'yshift=-8cm') +
  tex_scope(fig4_tex, 'xshift=10cm, yshift=-8cm') +
  tex_scope(fig5_tex, 'yshift=-16cm') +
  tex_scope(fig6_tex, 'xshift=10cm, yshift=-16cm') +
  tex_scope(fig7_tex, 'yshift=-24cm') +
  tex_scope(fig8_tex, 'xshift=10cm, yshift=-24cm') +
  r'\node[anchor=south west] (0, 0) {L = grey, R = white, S = blue, C-S = pink, edges = L-adjacency};',
  columns=2
) +
r'''\end{tikzpicture}
\end{document}
'''
)

with open(TEXFILE, 'w', encoding='utf-8') as f:
    f.write(TEX)
subprocess.run(f'pdflatex -interaction=nonstopmode {TEXFILE}', check=True)
