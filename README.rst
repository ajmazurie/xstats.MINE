xstats.MINE
===========

``xstats.MINE`` is a `Python <http://www.python.org/>`_ library wrapping the Maximal Information-based Nonparametric Exploration (`MINE <http://www.exploredata.net/>`_) statistical library which is, for now, only available as a Java implementation.

``xstats.MINE`` can be used both with the `Jython <http://www.jython.org>`_ interpreter or with Python using `JPype <http://jpype.sourceforge.net/>`_.

MINE is a set of statistics that can be used to identify important relationships in datasets and characterize these relationships. Given a relationship between two vectors of scalars, MINE produces the following scores:

- MIC (maximum information coefficient), which captures relationship strength
- MAS (maximum asymmetry score), which captures departure from monotonicity
- MEV (maximum edge value), which captures closeness to being a function
- MCN (minimum cell number), which captures complexity

A complete description of MINE and examples of use can be found in the following article: D. Reshef, Y. Reshef, H. Finucane, S. Grossman, G. McVean, P. Turnbaugh, E. Lander, M. Mitzenmacher, P. Sabeti. Detecting novel associations in large datasets. Science 334, 6062 (2011).

**Contact** Aurelien Mazurie <ajmazurie@oenone.net>

**Keywords** Python, MINE, statistics

Installation
------------

If you plan to use **xstats.MINE** with the Jython interpreter you need to ensure the **MINE.jar** file (which you can retrieve at http://www.exploredata.net/Downloads/MINE-Application) is visible from Jython. For example, ::

	jython -Dpython.path=MINE.jar my_script.py

will execute your script **my_script.py** with Jython while loading the **MINE.jar** file located in the current directory.

If you plan to use **xstats.MINE** with the Python interpreter you need to install the JPype library first. An easy way to do so, if you have **setuptools** installed, is to type ::

	easy_install JPype

(see the relevant `documentation <http://pypi.python.org/pypi/setuptools>`_)

Finally, to install **xstats.MINE** itself please follow those steps:

- Download the latest version of the library from http://github/ajmazurie/xstats.MINE/downloads
- Unzip the downloaded file, and ``cd`` in the resulting directory
- Run ``python setup.py install``

Note that **xstats.MINE** has been tested with the version 1.0.1b of **MINE.jar**; previous versions would fail.

Examples
--------

Example #1: MINE on a pair of scalars
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The method **analyze_pair()** can be used to calculate the various MINE scores on a pair of scalar vectors. For example, ::

	import xstats.MINE

	x = [40,50,None,70,80,90,100,110,120,130,140,150,
		 160,170,180,190,200,210,220,230,240,250,260]

	y = [-0.07,-0.23,-0.1,0.03,-0.04,None,-0.28,-0.44,-0.09,0.12,0.06,
		 -0.04,0.31,0.59,0.34,-0.28,-0.09,-0.44,0.31,0.03,0.57,0,0.01]

	print "x y", xstats.MINE.analyze_pair(x, y)

will return the following scores::

	{'MCN': 2.5849625999999999,
	 'MAS': 0.040419996,
	 'pearson': 0.31553724,
	 'MIC': 0.38196000000000002,
	 'MEV': 0.27117000000000002,
	 'non_linearity': 0.28239626000000001}

Example #2: MINE on a file
~~~~~~~~~~~~~~~~~~~~~~~~~~

The method **analyze_file()** can be used to calculate the various MINE scores on values read from a comma- or tab-delimited file. The function can consider all pairs of variables in the file, only adjacent variables, or compare all variables in turn against a master variable.

If the input file has a **.csv** extension the function will assume it is a `comma-delimited file <http://en.wikipedia.org/wiki/Comma-separated_values>`_; if not it assumes it is a tab-delimited file.

For example, analyzing the **Spellman.csv** file which can be found at http://www.exploredata.net/Downloads/Gene-Expression-Data-Set ::

	import xstats.MINE

	for a, b, scores in xstats.MINE.analyze_file("Spellman.csv", xstats.MINE.MASTER_VARIABLE, 0, cv = 0.7):
		print a, b, scores

will display the following (only the first lines are shown; lines are truncated)::

	time YER044C {'MCN': 2.5849625999999999, 'MAS': 0.16225999999999999, ...}
	time YNL178W {'MCN': 2.5849625999999999, 'MAS': 0.46802998000000001, ...}
	time YCR098C {'MCN': 2.0, 'MAS': 0.0, ...}
	time YEL050C {'MCN': 2.0, 'MAS': 0.0, ...}

Note that this example replicates the one shown in the MINE documentation::

	java -jar MINE.jar Spellman.csv 0 cv=0.7

(see http://www.exploredata.net/Usage-instructions/Parameters)
