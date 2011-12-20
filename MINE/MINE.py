
from . import python_implementation
import sys, os

# if ran under Jython, load MINE directly
is_jython = (python_implementation() == "JYTHON")

if (is_jython):
	import data.Dataset as Dataset
	import analysis.Analysis as Analysis
	import main.BriefResult as Result
	import main.Analyze as Analyze

	import java.io.BufferedWriter
	import java.io.OutputStreamWriter
	process_output = java.io.BufferedWriter(java.io.OutputStreamWriter(sys.stdout))

# if ran under Python, use JPype to load MINE
else:
	import jpype
	jpype.startJVM(jpype.getDefaultJVMPath())
	Dataset = jpype.JPackage("data.Dataset")
	Analysis = jpype.JPackage("analysis.Analysis")
	Result = jpype.JPackage("main.BriefResult")
	Analyze = jpype.JPackage("main.Analyze")

	process_output = sys.stdout

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

MASTER_VARIABLE = 0
ALL_PAIRS = 1
ADJACENT_PAIRS = 2

def MINE (fn,
	method = None, master_variable = None,
	permute_data = False,
	required_common_vals_fraction = 0.0,
	max_num_boxes_exponent = 0.6,
	num_clumps_factor = 15,
	debug_level = 0):
	""" Execute MINE on a comma- or tab-delimited file

	Arguments:
		- *fn* name of the input file (mandatory)

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

	if (debug_level < 0) or (debug_level > 4):
		raise ValueError("Invalid debug level: %s (must be between 0 and 4)" % debug_level)

	dataset = Dataset(fn, debug_level, process_output)

	if (method == ALL_PAIRS):
		analysis = Analysis(dataset, Analysis.AnalysisStyle.allPairs)

	elif (method == ADJACENT_PAIRS):
		analysis = Analysis(dataset, Analysis.AnalysisStyle.adjacentPairs)

	elif (method == MASTER_VARIABLE):
		analysis = Analysis(dataset, master_variable)

	results = analysis.getSortedResults(Result, fn,
		required_common_vals_fraction,
		max_num_boxes_exponent,
		num_clumps_factor,
		sys.maxint, # gcWait
		"dummy", # jobID
		debug_level,
		process_output
	)

	Analyze.printResults(results, fn, "dummy")
