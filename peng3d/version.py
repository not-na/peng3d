#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py
#
#  Copyright 2016-2022 notna <notna@apparat.org>
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

__all__ = ["VERSION", "RELEASE"]

VERSION: str = "1.12.0"
"""
Full version number, compliant with `semantic versioning <https://semver.org/>`_

Used to display the version in the title of the documentation.

Also used for the version in ``setup.py``\\ .

.. versionchanged:: 1.10.0
    Before 1.10.0, ``peng3d`` did not quite comply with semantic versioning.
    This is mainly due to the ``a1`` suffix on most version names.
"""

RELEASE: str = "1.12.0"
"""
Currently the same as :py:data:`VERSION`\\ .

Used to display the version on the top-right of the documentation.
"""
