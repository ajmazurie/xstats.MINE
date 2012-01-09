
from . import python_implementation
import sys, os, csv, tempfile

is_jython = (python_implementation() == "JYTHON")

# this library run under Jython
if (is_jython):
	import java

	# access to MINE packages
	import data.Dataset as Dataset
	import analysis.Analysis as Analysis
	import main.BriefResult as Result
	import main.Analyze as Analyze

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
	Dataset = jpype.JClass("data.Dataset")
	Analysis = jpype.JClass("analysis.Analysis")
	Result = jpype.JClass("main.BriefResult")
	Analyze = jpype.JClass("main.Analyze")

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

def analyze_pair (x, y, cv = 0.0, exp = 0.6, c = 15, missing_value = None):
	""" Calculate various MINE statistics on a relationship between two scalar vectors

	Arguments:
		- **x** first vector
		- **y** second vector
		- **cv** from MINE: 'floating point number indicating which percentage of
			the records need to have data in them for both variables before those
			two variables are compared'; i.e., the minimum percent overlap between
			the two input vectors after discounting missing values (default: 0.0)
		- **exp** from MINE: 'exponent of the equation B(n) = n^alpha' (default: 0.6)
		- **c** from MINE: 'determine by what factor clumps may outnumber columns
			when OptimizeXAxis is called. When trying to partition the x-axis into
			x columns, the algorithm will start with at most cx clumps' (default: 15)
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

	if (is_jython):
		xy = (x, y)
	else:
		xy = jpype.JArray(jpype.JFloat, 2)((x, y))

	_silence_output()

	dataset = Dataset(xy, 0, _null_buffered_writer)

	result = dataset.getResult(
		Result, # BriefResult class
		0, 1, # first and second variables in the dataset
		float(cv), float(exp), float(c), # MINE parameters
		0, _null_buffered_writer # debug level, debug stream
	)

	_restore_output()

	keys = ("MIC", "non_linearity", "MAS", "MEV", "MCN", "pearson")
	values = result.toString().split(',')[2:]

	result_ = {}
	for key, value in zip(keys, values):
		if (value == ''):
			value = None
		elif (value == "ERROR"):
			value = None
		else:
			value = float(value)

		result_[key] = value

	return result_

MASTER_VARIABLE = 0
ALL_PAIRS = 1
ADJACENT_PAIRS = 2

def analyze_file (fn,
	method = None, master_variable = None,
	permute_data = False,
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
		- **permute_data** (from MINE:) "instructs MINE to permute the dataset
			before running it. If **method** is set to ADJACENT_PAIRS, then every
			other variable will be permuted. If it is set to MASTER_VARIABLE, all
			variables except for the master variable will be permuted. It cannot
			be set with ALL_PAIRS" (default: False)
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

	if (permute_data) and (method == ALL_PAIRS):
		raise ValueError("permute_data cannot be used with the ALL_PAIRS method")

	_silence_output()

	dataset = Dataset(fn, 0, _null_buffered_writer)

	if (method == ALL_PAIRS):
		analysis = Analysis(dataset, Analysis.AnalysisStyle.allPairs)

	elif (method == ADJACENT_PAIRS):
		analysis = Analysis(dataset, Analysis.AnalysisStyle.adjacentPairs)

	elif (method == MASTER_VARIABLE):
		analysis = Analysis(dataset, int(master_variable))

	if (permute_data):
		if (method == ADJACENT_PAIRS):
			for v in range(0, dataset.numVariables() / 2):
				dataset.permuteVariable(2 * v)

		elif (method == MASTER_VARIABLE):
			for v in range(0, dataset.numVariables()):
				if (v != dataset.getMasterVariableId()):
					dataset.permuteVariable(v)

	fn = tempfile.NamedTemporaryFile('w')

	results = analysis.getSortedResults(
		Result, fn.name,
		float(cv), float(exp), float(c), # MINE parameters
		2147483647, # gcWait
		"dummy", # jobID
		0, _null_buffered_writer # debug level, debug stream
	)

	_restore_output()

	fn = tempfile.NamedTemporaryFile('w', delete = False)
	fn_ = fn.name + ",dummy,Results.csv"

	Analyze.printResults(results, fn.name, "dummy")

	fn.close()

	for entry in csv.DictReader(open(fn_, 'rU')):
		yield entry["X var"], entry["Y var"], {
			"MIC": float(entry["MIC (strength)"]),
			"non_linearity": float(entry["MIC-p^2 (nonlinearity)"]),
			"MAS": float(entry["MAS (non-monotonicity)"]),
			"MEV": float(entry["MEV (functionality)"]),
			"MCN": float(entry["MCN (complexity)"]),
			"pearson": float(entry["Linear regression (p)"])
		}

	os.unlink(fn.name)
