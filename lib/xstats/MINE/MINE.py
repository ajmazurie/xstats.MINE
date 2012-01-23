
tested_MINE_version = "1.0.1d" # last version or MINE.jar against which xstats.MINE has been tested

from . import python_implementation
import sys, os, csv, tempfile

is_jython = (python_implementation() == "JYTHON")

# this library run under Jython
if (is_jython):
	import java

	# access to MINE packages
	try:
		import main.styles.AllPairsAnalysisStyle as AllPairsAnalysisStyle
		import analysis.Analysis as Analysis
		import analysis.AnalysisParameters as AnalysisParameters
		import main.Analyze as Analyze
		import main.styles.ConsecutivePairsAnalysisStyle as ConsecutivePairsAnalysisStyle
		import data.Dataset as Dataset
		import main.styles.MasterVariableAnalysisStyle as MasterVariableAnalysisStyle
		import mine.core.MineParameters as MineParameters
		import analysis.results.BriefResult as Result
		import data.VarPairData as VarPairData
		import analysis.VarPairQueue as VarPairQueue

	except Exception, e:
		raise Exception("Unable to load MINE.jar classes (%s)" % e)

	# hook for stdout
	class null_output_stream (java.io.OutputStream):
		def write (self, b, off, len):
			pass
	_null_output_stream = null_output_stream()

# this library run under Python
else:
	import jpype
	jpype.startJVM(
		jpype.getDefaultJVMPath(),
		"-Djava.class.path=" + os.environ.get("CLASSPATH", os.getcwd())
	)
	java = jpype.java

	# access to MINE packages
	try:
		AllPairsAnalysisStyle = jpype.JClass("main.styles.AllPairsAnalysisStyle")
		Analysis = jpype.JClass("analysis.Analysis")
		AnalysisParameters = jpype.JClass("analysis.AnalysisParameters")
		Analyze = jpype.JClass("main.Analyze")
		ConsecutivePairsAnalysisStyle = jpype.JClass("main.styles.ConsecutivePairsAnalysisStyle")
		Dataset = jpype.JClass("data.Dataset")
		MasterVariableAnalysisStyle = jpype.JClass("main.styles.MasterVariableAnalysisStyle")
		MineParameters = jpype.JClass("mine.core.MineParameters")
		Result = jpype.JClass("analysis.results.BriefResult")
		VarPairData = jpype.JClass("data.VarPairData")
		VarPairQueue = jpype.JClass("analysis.VarPairQueue")

	except jpype.JavaException, e:
		raise Exception("Unable to load MINE.jar classes (%s)" % e.message())

	# test the MINE.jar version
	from pkg_resources import parse_version

	try:
		current_MINE_version = Analyze.versionDescription().split(' ')[-1]
	except:
		raise Exception("Unable to determine the MINE.jar version")

	current_MINE_version_ = parse_version(current_MINE_version)
	tested_MINE_version_ = parse_version(tested_MINE_version)

	if (current_MINE_version_ < tested_MINE_version_):
		raise Exception("xstats.MINE requires MINE.jar version %s or above (current version is %s)" % (tested_MINE_version, current_MINE_version))

	if (current_MINE_version_ > tested_MINE_version_):
		print >>sys.stderr, "WARNING: xstats.MINE has not been tested on MINE.jar version %s" % current_MINE_version

	# hook for stdout
	_null_output_stream = jpype.JClass("org.apache.commons.io.output.NullOutputStream")()

# we need to set up hooks for the standard output, as MINE
# will send text to it even when no warning or error occurs
_original_print_stream = java.lang.System.out
_null_print_stream = java.io.PrintStream(_null_output_stream)
_null_buffered_writer = java.io.BufferedWriter(java.io.OutputStreamWriter(_null_output_stream))

def _silence_output():
	java.lang.System.setOut(_null_print_stream)

def _restore_output():
	java.lang.System.setOut(_original_print_stream)

NaN = float("NaN")

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def analyze_pair (x, y, exp = 0.6, c = 15, missing_value = None):
	""" Calculate various MINE statistics on a relationship between two scalar vectors

	Arguments:
		- **x** first vector
		- **y** second vector
		- **exp** (from MINE:) "exponent of the equation B(n) = n^alpha" (default: 0.6)
		- **c** (from MINE:) "determine by what factor clumps may outnumber columns
			when OptimizeXAxis is called. When trying to partition the x-axis into
			x columns, the algorithm will start with at most cx clumps" (default: 15)
		- **missing_value** value to be considered missing value in x and y (default: None)

	Return:
		- dictionary with keys 'MIC', 'non_linearity', 'MAS', 'MEV', 'MCN' and 'pearson'
			corresponding to the maximum information coefficient, non-linearity,
			maximum asymmetry score, maximum edge value, minimum cell number and Pearson
			correlation coefficient, respectively

	Notes:
		- the two input vectors must be of equal length
		- missing values in either x or y must be reported as missing_value values

	See: D. Reshef, Y. Reshef, H. Finucane, S. Grossman, G. McVean, P. Turnbaugh,
	E. Lander, M. Mitzenmacher, P. Sabeti. Detecting novel associations in large
	datasets. Science 334, 6062 (2011).
	"""
	if (len(x) != len(y)):
		raise ValueError("The two vectors must be of equal length")

	# convert missing values
	x = [NaN if (item == missing_value) else item for item in x]
	y = [NaN if (item == missing_value) else item for item in y]

	if (not is_jython):
		x = jpype.JArray(jpype.JFloat, 1)(x)
		y = jpype.JArray(jpype.JFloat, 1)(y)

	_silence_output()

	dataset = VarPairData(x, y)

	parameters = MineParameters(
		float(exp), float(c),
		0, _null_buffered_writer # debug level, debug stream
	)

	result = Analysis.getResult(Result, dataset, parameters)

	_restore_output()

	keys = ("MIC", "non_linearity", "MAS", "MEV", "MCN", "pearson")
	values = result.toString().split(',')[2:]

	result_ = {}
	for key, value in zip(keys, values):
		if (value == '') or (value == "ERROR"):
			value = None
		else:
			value = float(value)

		result_[key] = value

	return result_

MASTER_VARIABLE = 0
ALL_PAIRS = 1
ADJACENT_PAIRS = 2

def analyze_file (fn,
	method = None,
	master_variable = None,
	cv = 0.0, exp = 0.6, c = 15):
	""" Calculate MINE statistics on a comma- or tab-delimited file

	Arguments:
		- **fn** name of the input file; must have a .csv or .txt extension to
			distinguish between comma- or tab-delimited format, respectively
		- **method** determine which variable MINE will compare to each other;
			either MASTER_VARIABLE (compare all variables against one master
			variable), ALL_PAIRS (compare all pairs of variables against each
			other), or ADJACENT_PAIRS (compare consecutive pairs of variables)
		- **master_variable** index of the master variable; only considered
			if **method** is set to MASTER_VARIABLE
		- **cv** (from MINE:) "floating point number indicating which percentage of
			the records need to have data in them for both variables before those
			two variables are compared"; i.e., the minimum percent overlap between
			the two input vectors after discounting missing values (default: 0.0)
		- **exp** (from MINE:) "exponent of the equation B(n) = n^alpha" (default: 0.6)
		- **c** (from MINE:) "determine by what factor clumps may outnumber columns
			when OptimizeXAxis is called. When trying to partition the x-axis into
			x columns, the algorithm will start with at most cx clumps" (default: 15)

	See: D. Reshef, Y. Reshef, H. Finucane, S. Grossman, G. McVean, P. Turnbaugh,
	E. Lander, M. Mitzenmacher, P. Sabeti. Detecting novel associations in large
	datasets. Science 334, 6062 (2011).
	"""

	if (not os.path.exists(fn)):
		raise ValueError("Unknown file '%s'" % fn)

	if (method is None):
		raise ValueError("A method must be specified; accepted values are MASTER_VARIABLE, ALL_PAIRS or ADJACENT_PAIRS")

	elif (method not in (MASTER_VARIABLE, ALL_PAIRS, ADJACENT_PAIRS)):
		raise ValueError("Invalid method: %s" % method)

	if (method == MASTER_VARIABLE) and (master_variable is None):
		raise ValueError("A master variable must be provided when using the MASTER_VARIABLE method")

	parameters = AnalysisParameters(
		MineParameters(
			float(exp), float(c),
			0, _null_buffered_writer # debug level, debug stream
		),
		float(cv),
		2147483647 # gcWait
	)

	_silence_output()

	# replicate behavior of main.Analyze.runAnalysis()
	dataset = Dataset(fn, 0)
	pair_queue = VarPairQueue(dataset)

	if (method == ALL_PAIRS):
		analysis_style = AllPairsAnalysisStyle()

	elif (method == ADJACENT_PAIRS):
		analysis_style = ConsecutivePairsAnalysisStyle()

	elif (method == MASTER_VARIABLE):
		analysis_style = MasterVariableAnalysisStyle(int(master_variable))

	analysis_style.addVarPairsTo(pair_queue, dataset.numVariables())
	analysis = Analysis(dataset, pair_queue)

	while (not analysis.varPairQueue().isEmpty()):
		analysis.analyzePairs(Result, parameters, 100)

	_restore_output()

	keys = ("MIC", "non_linearity", "MAS", "MEV", "MCN", "pearson")

	# replicate behavior of main.Analyze.printResults()
	for entry in analysis.getSortedResults():
		if (not entry.worthMentioning()):
			continue

		values = entry.toString().split(',')

		result = {}
		for key, value in zip(keys, values[2:]):
			if (value == '') or (value == "ERROR"):
				value = None
			else:
				value = float(value)

			result[key] = value

		yield values[0], values[1], result
