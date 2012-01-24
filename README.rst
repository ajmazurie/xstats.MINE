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

**Keywords** MINE, Statistics, Python, Jython, JPype

Installation
------------

Please follow those steps to ensure a proper installation of ``xstats.MINE``; note that step 3 can be skipped if you only intent to use ``xstats.MINE`` with Jython.

1. Installation of MINE.jar
~~~~~~~~~~~~~~~~~~~~~~~~

The file **MINE.jar**, which you can retrieve at http://www.exploredata.net/Downloads/MINE-Application must be downloaded in your computer. It is advised to place this file in a stable location; e.g., a directory on your computer dedicated to Java `.jar files <http://en.wikipedia.org/wiki/JAR_(file_format)>`_.

Once downloaded, **MINE.jar** must be made visible from the Java interpreter that lies behind Jython and JPype. It typically means adding the path to this file (wherever you placed it) to the ``CLASSPATH`` environment variable. If you are not familiar with the concept of environment variable, a quick introduction is available `here <http://docs.oracle.com/javase/tutorial/essential/environment/paths.html>`_.

Depending of if you are under Windows or a flavor of Unix the technique to modify the ``CLASSPATH`` slightly differs. A good tutorial is available `here <http://docs.oracle.com/javase/tutorial/essential/environment/paths.html>`_; simply replaces references to ``PATH`` by references to ``CLASSPATH``.

Please note that this version of ``xstats.MINE`` is compatible with ``MINE.jar`` version 1.0.1b through 1.0.1d.

2. Installation of JPype
~~~~~~~~~~~~~~~~~~~~~~~~

If you plan to use ``xstats.MINE`` with Python you need to have JPype installed first. An easy way to do so, if you have **setuptools** installed, is to type ::

	easy_install JPype

(see the relevant `documentation <http://pypi.python.org/pypi/setuptools>`_)

You will also need to download the **commons-io-X.X.jar** file from http://commons.apache.org/io/; X.X is the version of the Commons IO library (2.1 at the time of writing). This file must be declared in your ``CLASSPATH`` the same way you did for **MINE.jar**; see instructions in Step 1.

3. Installation of xstats.MINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, to install ``xstats.MINE`` for both Python and Jython please follow those steps:

- Download the latest version of the library from http://github/ajmazurie/xstats.MINE/downloads
- Unzip the downloaded file, and ``cd`` in the resulting directory
- Run ``python setup.py install``

To update ``xstats.MINE`` with newer versions just repeat Step 3.

Examples of use
---------------

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

Note that this example replicates the one shown in the MINE documentation (see http://www.exploredata.net/Usage-instructions/Parameters)::

	java -jar MINE.jar Spellman.csv 0 cv=0.7

Licensing
---------

``xstats.MINE`` is released under a `MIT/X11 license <http://en.wikipedia.org/wiki/MIT_License>`_.

``MINE.jar`` is released under a `Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported <http://creativecommons.org/licenses/by-nc-nd/3.0/>`_ license by its authors.
