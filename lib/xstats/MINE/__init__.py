
def python_implementation():
	# Python 2.6+ or Jython 2.6+
	try:
		import platform
		return platform.python_implementation().upper()
	except:
		pass

	# Python 2.3+
	try:
		import platform
		if ("java" in platform.system().lower()):
			return "JYTHON"
	except:
		pass

	import sys

	if ("java" in sys.platform.lower()):
		return "JYTHON"

	elif ("cli" in sys.platform.lower()):
		return "IRONPYTHON"

	else:
		return "CPYTHON"

from MINE import *