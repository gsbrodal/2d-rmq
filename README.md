# The Encoding Complexity of Two Dimensional Range Minimum Data Structures

This is a proof-of-concept implementation in Python 3.15 of matrix encoding 
schemes supporting range minimum queries from the following paper.

* [1] _The Encoding Complexity of Two Dimensional Range Minimum Data Structures_,
  by Gerth Stølting Brodal, Andrej Brodnik and Pooya Davoodi.
  In Proc. 21st Annual European Symposium on Algorithms, 
  Lecture Notes in Computer Science, vol 8125, 229-240, Springer, 2013.
  DOI: [10.1007/978-3-642-40450-4_20](https://dx.doi.org/10.1007/978-3-642-40450-4_20)

* [2] _The Encoding Complexity of Two Dimensional Range Minimum Data Structures_,
  by Gerth Stølting Brodal, Andrej Brodnik and Pooya Davoodi.
  arXiv 2026.

Two encoding schemes are implemented for _m_ x _n_ matrices, 
achieving respectively encodings of size 

* `suboptimal_codec.py` : O(_m_ ⋅ _n_ ⋅ (log _m_ + (log(_m_ ⋅ _n_))/&alpha; + log &alpha;)) bits.
* `optimal_codec.py`    : O(_m_ ⋅ _n_ ⋅ log _m_) bits.

Decoding times are linear. Encoding times are slow and is superlinear. The
asymptotic optimal encoder can encode matrices with sizes of the order 10 x 50 in
a few seconds, whereas the suboptimal encoder can encode matrices with sizes of
the order 100 x 300 in a few seconds.

The stress tests performed naively checks all possible range minimum queries in 
time O(_n_<sup>3</sup> ⋅ _m_<sup>3</sup>) if the answer is the same before and after encoding-decoding.

## Files

The folder contains the following Python 3.15 files:

* `main.py` main file, performing stress tests of the two codecs and generates
  latex tikz figures for the optimal encoding.

* `matrix_codec.py` abstract class for matrix codecs.

* `suboptimal_codec.py` implementation of the codec in [2, Section 3].

* `optimal_codec.py` implementation of the codec in [2, Section 5]

* `test_rmq.py` integrity tests of encoding and decoding matrices.

* `bit_sequence.py` class implementing iterable sequences of bits.

* `encoding_utils.py` functions to encode and decode integers and tree structures.

* `matrix.py` simple implementation of a matrix supporting M[i, j] indexing.

* `tree.py` class implementing navigational static trees 
  with annotations of internal node with the rank of the leftmost leaf.

* `matrix_cells` class supporting L-adjacency among matrix indices under deletions from L.

* `word_functions.py` functions on words/integers, like computing msb_bit(word).

* `interval_union_find.py` interval union find structure supporting deletions 
  in amortized O(1) time and successor/predecessor queries in O(1) time.

* `connected_components.py` find connected components in a graph.

* `figure_optimal_codec.py` generate tikz figure of last encoding created by `optimal_codec.py`.

* `figure_partition.py` stand alone program to create a tikz figure of the partitioning of a matrix.

Copyright Gerth Stølting Brodal, Aarhus University, 2026.
