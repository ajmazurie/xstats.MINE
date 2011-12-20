xstats.MINE
===========

``xstats.MINE`` is a `Python <http://www.python.org/>`_ library wrapping the **M**aximal **I**information-based **N**onparametric **E**xploration (`MINE <http://www.exploredata.net/>`_ statistical library which is, for now, only available as a Java implementation. ``xstats.MINE`` can be used both with the `Jython <http://www.jython.org>`_ interpreter or with Python using `JPype <http://jpype.sourceforge.net/>`_.

MINE is a set of statistics that can be used to identify important relationships in datasets and characterize these relationships. Given a relationship between two vectors of scalars, MINE produces the following scores:

- MIC (maximum information coefficient), which captures relationship strength
- MAS (maximum asymmetry score), which captures departure from monotonicity
- MEV (maximum edge value), which captures closeness to being a function
- MCN (minimum cell number), which captures complexity

A complete description of MINE and examples of use can be found in the following article: D. Reshef, Y. Reshef, H. Finucane, S. Grossman, G. McVean, P. Turnbaugh, E. Lander, M. Mitzenmacher, P. Sabeti. Detecting novel associations in large datasets. Science 334, 6062 (2011).

**Contact** Aurelien Mazurie <ajmazurie@oenone.net>
**Keywords** Python, MINE, statistics
