#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  peng.py
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

__all__ = ["Peng"]

import sys

#from . import window, config, keybind, pyglet_patch
from . import config, world

_pyglet_patched = sys.version_info.major == 2 or not world._have_pyglet

class Peng(object):
    """
    This Class should only be instatiated once per application, if you want to use multiple windows, see :py:meth:`createWindow()`\ .
    
    An Instance of this class represents the whole Engine, with all accompanying state and window/world objects.
    
    Be sure to keep your instance accessible, as it will be needed to create most other classes.
    """
    
    def __init__(self,cfg={}):
        global _pyglet_patched
        if world._have_pyglet:
            from . import pyglet_patch, keybind # Local import for compat with headless machines
        self.window = None
        
        self.eventHandlers = {}
        
        if cfg == {}:
            cfg = {} # To avoid bugs with default arguments
        self.cfg = config.Config(cfg,defaults=config.DEFAULT_CONFIG)
        if world._have_pyglet:
            self.keybinds = keybind.KeybindHandler(self)
        
        if not _pyglet_patched and self.cfg["pyglet.patch.patch_float2int"]:
            _pyglet_patched = True
            pyglet_patch.patch_float2int()
    
    def createWindow(self,cls=None,*args,**kwargs):
        """
        createWindow(cls=window.PengWindow, *args, **kwargs)
        
        Creates a new window using the supplied ``cls``\ .
        
        If ``cls`` is not given, :py:class:`peng3d.window.PengWindow()` will be used.
        
        Any other positional or keyword arguments are passed to the class constructor.
        
        Note that this method currently does not support using multiple windows.
        
        .. todo::
           
           Implement having multiple windows.
        """
        if cls is None:
            from . import window
            cls = window.PengWindow
        if self.window is not None:
            raise RuntimeError("Window already created!")
        self.window = cls(self,*args,**kwargs)
        return self.window
    
    def run(self):
        """
        Runs the application main loop.
        
        This method is blocking and needs to be called from the main thread to avoid OpenGL bugs that can occur.
        """
        self.window.run()
    
    def handleEvent(self,event_type,args,window=None):
        """
        Handles a pyglet event.
        
        This method is called by :py:meth:`PengWindow.dispatch_event()` and handles all events.
        
        See :py:meth:`registerEventHandler()` for how to listen to these events.
        """
        args = list(args)
        #if window is not None:
        #    args.append(window)
        if event_type not in ["on_draw","on_mouse_motion"] and self.cfg["debug.events.dump"]:
            print("Event %s with args %s"%(event_type,args))
        if event_type in self.eventHandlers:
            for handler in self.eventHandlers[event_type]:
                handler(*args)
    def registerEventHandler(self,event_type,handler):
        """
        Registers an event handler.
        
        The specified callable handler will be called everytime an event with the same ``event_type`` is encountered.
        
        All event arguments are passed as positional arguments.
        """
        if self.cfg["debug.events.register"]:
            print("Registered Event: %s Handler: %s"%(event_type,handler))
        if event_type not in self.eventHandlers:
            self.eventHandlers[event_type]=[]
        self.eventHandlers[event_type].append(handler)

class HeadlessPeng(object):
    pass
