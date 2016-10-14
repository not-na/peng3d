#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py
#  
#  Copyright 2016 notna <notna@apparat.org>
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

__all__ = ["VERSION","RELEASE"]

VERSION = "1.4.0a1"
"""
Full version number of format ``MAJOR.MINOR.BUGFIX(a|b|pre)SUBRELEASE`` where major is increased only on very major feature changes.
Minor is changed if a new feature is introduced or an API change is made, while bugfix only changes if an important bugfix needs to be provided before the next release.
Either a, b, or pre follows depending on the type of release, e.g. a for alpha, b for beta and pre for prereleases.

Used to display the version in the title of the documentation.

.. seealso::
   
   See the `Distutils docs on version numbers <https://docs.python.org/2/distutils/setupscript.html#additional-meta-data>`_ for more information.

"""

RELEASE = "1.4.0"
"""
Same as :py:data:`VERSION` but without the subrelease.

Used to display the version on the top-right of the documentation.
"""
