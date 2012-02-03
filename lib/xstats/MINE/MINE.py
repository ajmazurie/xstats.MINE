
import sys, os, csv, tempfile

MINE_version = "1.0.1d" # last version or MINE.jar against which xstats.MINE has been tested
MINE_modules = (
	("AllPairsAnalysisStyle", "main.styles.AllPairsAnalysisStyle"),
	("Analysis", "analysis.Analysis"),
	("AnalysisParameters", "analysis.AnalysisParameters"),
	("Analyze", "main.Analyze"),
	("ConsecutivePairsAnalysisStyle", "main.styles.ConsecutivePairsAnalysisStyle"),
	("Dataset", "data.Dataset"),
	("MasterVariableAnalysisStyle", "main.styles.MasterVariableAnalysisStyle"),
	("MineParameters", "mine.core.MineParameters"),
	("Result", "analysis.results.BriefResult"),
	("VarPairData", "data.VarPairData"),
	("VarPairQueue", "analysis.VarPairQueue")
)

# determine the environment
try:
	import java
	environment = "JYTHON"
except:
	try:
		import jpype
		environment = "PYTHON"
	except:
		raise Exception("JPype library not found")

# this library run under Jython
if (environment == "JYTHON"):
	# access to MINE packages
	for (module_alias, module_name) in MINE_modules:
		try:
			globals()[module_alias] = __import__(module_name, fromlist = [module_alias])

		except ImportError, e:
			raise Exception("Unable to load MINE.jar class %s (%s)" % (module_name, e))

	# hook for stdout
	class null_output_stream (java.io.OutputStream):
		def write (self, b, off, len):
			pass
	_null_output_stream = null_output_stream()

	environment = "JYTHON"

# this library run under Python
elif (environment == "PYTHON"):
	# launch the Java virtual machine
	JVM = jpype.getDefaultJVMPath()
	JVM_options = ["-Djava.class.path=" + os.environ.get("CLASSPATH", os.getcwd())]

	if (JVM is None) or (not os.path.exists(JVM)):
		JAVA_HOME = os.getenv("JAVA_HOME")

		if (JAVA_HOME is None):
			raise Exception("Unable to find a Java runtime to use; please set your JAVA_HOME to the correct location")

		# attempt to salvage JVM when under Windows; see neo4j._backend code
		if (sys.platform == "win32"):
			if (os.path.exists(JAVA_HOME + "/bin/javac.exe")):
				JAVA_HOME += "/jre"

			for fn in ("/bin/client/jvm.dll", "/bin/server/jvm.dll"):
				if (os.path.exists(JAVA_HOME + fn)):
					JVM = JAVA_HOME + fn

	if (JVM is None) or (not os.path.exists(JVM)):
		raise Exception("Unable to find a Java runtime to use; JAVA_HOME appears to be set to an incorrect location (%s)" % JAVA_HOME)

	try:
		jpype.startJVM(JVM, *JVM_options)

	except Exception, e:
		raise Exception("Unable to start the JVM (%s)" % e)

	java = jpype.java

	# access to MINE packages
	for (module_alias, module_name) in MINE_modules:
		try:
			globals()[module_alias] = jpype.JClass(module_name)

		except jpype.JavaException, e:
			raise Exception("Unable to load MINE.jar class %s (%s)" % (module_name, e.message()))

	# test the MINE.jar version
	try:
		from pkg_resources import parse_version
		MINE_current_version = Analyze.versionDescription().split(' ')[-1]

		MINE_current_version_ = parse_version(MINE_current_version)
		MINE_version_ = parse_version(MINE_version)

	except:
		raise Exception("Unable to determine the MINE.jar version")

	if (MINE_current_version_ < MINE_version_):
		raise Exception("xstats.MINE requires MINE.jar version %s or above (current version is %s)" % (MINE_version, MINE_current_version))

	if (MINE_current_version_ > MINE_version_):
		print >>sys.stderr, "WARNING: xstats.MINE has not been tested on MINE.jar version %s" % MINE_current_version

	# hook for stdout
	try:
		_null_output_stream = jpype.JClass("org.apache.commons.io.output.NullOutputStream")()

	except jpype.JavaException, e:
		raise EXception("Unable to load commons-io.jar classes (%s)" % e.message())

	environment = "PYTHON"

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

	if (environment == "PYTHON"):
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
