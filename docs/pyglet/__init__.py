#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

from unittest.mock import Mock

from . import window
from . import gl
from . import graphics

"""class Mock(object):
    def __init__(self, *args,**kwargs):
        pass

    def __getattr__(self, name):
        return Mock()
    def __call__(self,*args,**kwargs):
        return Mock()
    def __getitem__(self,*args,**kwargs):
        return Mock()
    def __setitem__(self,*args,**kwargs):
        pass
    def __in__(self,*args,**kwargs):
        pass"""

lib = Mock()
text = Mock()
image = Mock()
compat_platform = "linux"
