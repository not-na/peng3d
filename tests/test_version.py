#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_version.py
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

# Probably not needed, but here anyway

import re

import peng3d

VERSION_PATTERN = r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{0,2}[a-z][0-9]{1,2}"

RELEASE_PATTERN = r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{0,2}"

def test_version_relation():
    assert peng3d.version.VERSION.startswith(peng3d.version.RELEASE)

def test_version_version_regex():
    assert re.match(VERSION_PATTERN,peng3d.version.VERSION)

def test_version_release_regex():
    assert re.match(RELEASE_PATTERN,peng3d.version.RELEASE)
