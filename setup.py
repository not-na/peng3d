#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#  
#  Copyright 2016-2021 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

# Distribution commands:
# python setup.py sdist bdist bdist_egg bdist_wheel
# outside venv:
# twine upload dist/*

# Test command:
# tox -- --x-display=$DISPLAY -v -m "'not graphical'"

#import peng3d.version as ver

import os
import sys
import importlib


spec = importlib.util.spec_from_file_location("peng3d.version",
                                              os.path.join("peng3d", "version.py")
                                              )
module = importlib.util.module_from_spec(spec)
sys.modules["peng3d.version"] = module
spec.loader.exec_module(module)

ver = module

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    longdesc = open("README.txt", "r").read()
except Exception:
    longdesc = "Python and pyglet based 3D Engine and toolkit"

setup(name='peng3d',
      version=ver.VERSION,
      description="Python and pyglet based 3D Engine and toolkit", # from the github repo
      long_description=longdesc,
      author="notna",
      author_email="notna@apparat.org",
      url="https://github.com/not-na/peng3d",
      packages=['peng3d',"peng3d.actor","peng3d.gui","peng3d.util"],
      install_requires=[
          "pyglet>=1.5.3",
          "bidict>=0.19.0",
      ],
      provides=["peng3d"],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        
        "License :: OSI Approved",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        
        ],
      )
