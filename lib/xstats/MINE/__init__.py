
__version_major__ = 0
__version_minor__ = 1
__revision__ = 1
__build__ = ""

version = "%s.%s (revision %s, build %s)" % (
	__version_major__,
	__version_minor__,
	__revision__,
	__build__
)

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