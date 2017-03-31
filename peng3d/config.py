#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config.py
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
import os

__all__ = ["CFG_FOG_DEFAULT","CFG_LIGHT_DEFAULT","DEFAULT_CONFIG","Config"]

def _get_script_home():
    # Docs removed to not show on autodoc
    # Integrated from pyglet.resource to also work on headless distributions
    # see http://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/programming_guide/resources.html
    frozen = getattr(sys, 'frozen', None)
    if frozen in ('windows_exe', 'console_exe'):
        return os.path.dirname(sys.executable)
    elif frozen == 'macosx_app':
        # py2app
        return os.environ['RESOURCEPATH']
    else:
        main = sys.modules['__main__']
        if hasattr(main, '__file__'):
            return os.path.dirname(os.path.abspath(main.__file__))
        else:
            # cx_Freeze
            return os.path.dirname(sys.executable)

    # Probably interactive
    return os.getcwd() # Always return a path

class Config(object):
    """
    Configuration object imitating a dictionary.
    
    ``config`` can be any dictionary-style object and is used to store the configuration set by the user.
    This object only needs to implement the ``__getitem__``\ , ``__setitem__`` and ``__contains__`` special methods.
    
    ``defaults`` can be any dictionary-style object and is only read from in case the ``config`` object does not contain the key.
    Every config object is stackable, e.g. you can pass another :py:class:`Config` object as the ``defaults`` object.
    
    Example for stacking configs::
       
       >>> myconf = Config()
       >>> myconf2 = Config(defaults=myconf)
       >>> myconf["foo"] = "bar"
       >>> print(myconf2["foo"])
       bar
       >>> myconf2["bar"] = "foo"
       >>> print(myconf2["bar"])
       foo
       >>> print(myconf["bar"])
       Traceback (most recent call last):
       ...
       KeyError: Key "bar" does not exist
    
    There is no limit in stacking configurations, though higher-stacked configs may get slow when defaulting due to propagating through the whole chain.
    """
    
    def __init__(self,config=None,defaults={}):
        if config is None:
            config = {} # To avoid bugs with defaulted arguments being initialized at load time, not object instantiation.
        self.config = config
        self.defaults = defaults
    def __getitem__(self,key):
        return self.config[key] if key in self.config else self.defaults[key]
    def __setitem__(self,key,value):
        self.config[key] = value
    def __contains__(self,key):
        return key in self.config

CFG_FOG_DEFAULT = {
    "enable":False,
    
    "color":None,
    "start":128,
    "end":128+32,
    }
"""
Default fog configuration.

This configuration simply disables fog.
"""

CFG_LIGHT_DEFAULT = {"enable":False}
"""
Default lighting configuration.

This configuration simply disables lighting.
"""

DEFAULT_CONFIG = {
    # graphics.*
    # OpenGL config
    "graphics.clearColor":(0.,0.,0.,1.),
    "graphics.wireframe":False,
    "graphics.fieldofview":65.0,
    "graphics.nearclip":0.1,
    "graphics.farclip":10000, # It's over 9000!
    "graphics.stencil.enable":False,
    "graphics.stencil.bits":8,
    "graphics.fogSettings":Config({},defaults=CFG_FOG_DEFAULT),
    "graphics.lightSettings":Config({},defaults=CFG_LIGHT_DEFAULT),
    
    # controls.*
    # Controls
    "controls.mouse.sensitivity":0.15,
    
    "controls.controls.movespeed":10.0,
    "controls.controls.verticalspeed":5.0,
    "controls.controls.forward":"w",
    "controls.controls.backward":"s",
    "controls.controls.strafeleft":"a",
    "controls.controls.straferight":"d",
    "controls.controls.jump":"space",
    "controls.controls.crouch":"lshift",
    "controls.keybinds.strict":False,
    "controls.keybinds.debug":False,
    
    "controls.keybinds.common.copy":"Ctrl-C",
    "controls.keybinds.common.paste":"Ctrl-V",
    "controls.keybinds.common.cut":"Ctrl-X",
    
    # debug.*
    # Debug config
    "debug.events.dump":False,
    "debug.events.logerr":False,
    "debug.events.register":False,
    
    # rsrc.*
    # Resource config
    "rsrc.enable":True,
    "rsrc.basepath":_get_script_home(),
    "rsrc.maxtexsize":1024, # Actual limit may be less, will be adjusted based on GL Capabilities
    
    # Other config options
    "pyglet.patch.patch_float2int":True,
}
"""
Default configuration values.

All default configuration values are stored here, for more information about specific config values, see :doc:`/configoption`\ .
"""
