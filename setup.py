#!/usr/bin/env python

try:
	from setuptools import setup, find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

setup(
	name = "xstats.MINE",
	version = "0.1",
	description = "Python wrapper for the MINE statistical library",
	long_description = open("README.rst").read(),
	url = "http://github.com/ajmazurie/xstats.MINE",
	license = open("LICENSE.txt").read(),

	author = "Aurelien Mazurie",
	author_email = "ajmazurie@oenone.net",

	namespace_packages = ["xstats"],
	packages = find_packages("lib"),
	package_dir = {'': "lib"},
)