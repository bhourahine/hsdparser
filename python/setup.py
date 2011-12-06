#!/usr/bin/env python3.1
from distutils.core import setup

setup(name="hsd",
      version="0.1",
      description="Parsing and processing framework for human-friendly "
        "structured data",
      author="Dennis Bredemeier, Bálint Aradi",
      author_email="dennis.bredemeier@gmail.com, baradi07@gmail.com",
      url="http://code.google.com/p/hsdparser/",
      license="MIT",
      platforms="platform independent",
      package_dir={"": "src"},
      packages=["hsd", "hsdnum", ],
      scripts=[],
      data_files=[("share/doc/hsd", ["LICENSE",])],
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
      long_description="""
Parsing and processing framework for human-friendly structured data
-------------------------------------------------------------------

The human-friendly structured data is a markup language with a light syntax,
making it ideal for config files, which need arbitrary number of nesting levels.
It can be two-way mapped onto a subset of XML.

This package provides utilites for parsing such data, converting it to an
XML-tree (using etree) and to query it.

Requires Python 3.1 or later.
"""
     )
