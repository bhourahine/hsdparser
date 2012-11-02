#!/usr/bin/env python3.2
from distutils.core import setup

setup(name="hsd",
      version="0.1",
      description="Parsing and processing framework for human-friendly "
        "structured data",
      author="Bálint Aradi, Dennis Bredemeier",
      author_email="baradi09@gmail.com",
      url="http://bitbucket.org/aradi/hsdparser",
      license="BSD",
      platforms="platform independent",
      package_dir={"": "src"},
      packages=["hsd", "hsdnum", ],
      scripts=[],
      data_files=[],
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      long_description="""
Human-friendly structured data (HSD)
====================================

The human-friendly structured data is a configuration markup language with a
light easy to read and easy to type syntax, making it ideal for config files
which must be created and edited by humans (such as input files for scientific
programs). It allows arbitrary number of nesting levels and can be two-way
mapped onto a subset of XML.

This project provides utilites for parsing such data, building a tree structure
out of it and to query it.
"""
     )
