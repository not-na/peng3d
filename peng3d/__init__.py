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

import sys

import warnings

if sys.version_info.major < 3:
    # needed for py27 compat
    import weakref as _weakref

    class _WeakMethod(object):
        """A callable object. Takes one argument to init: 'object.method'.
        Once created, call this object -- MyWeakMethod() --
        and pass args/kwargs as you normally would.
        """
        def __init__(self, object_dot_method):
            self.target = _weakref.proxy(object_dot_method.__self__)
            self.method = _weakref.proxy(object_dot_method.__func__)
            ###Older versions of Python can use 'im_self' and 'im_func' in place of '__self__' and '__func__' respectively

        def __call__(self):
            def f(*args,**kwargs):
                return self.method(self.target, *args, **kwargs)
            return f
    _weakref.WeakMethod = _WeakMethod

# These imports are here for convenience

from .peng import *
#from .window import *
from .layer import *
from .menu import *
from .camera import *
from .config import *
from .version import *
from .world import *
from .actor.player import *
from .actor import *
from .gui import *
from .gui.widgets import *
from .gui.button import *
from .gui.slider import *
from .gui.text import *
from .gui.container import *
from .gui.menus import *
from .resource import *
from .i18n import *
from .model import *
