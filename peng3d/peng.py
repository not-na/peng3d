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

import pyglet

from . import window, config, keybind


class Peng(object):
    """
    This Class should only be instatiated once per application, if you want to use multiple windows, see :py:meth:`createWindow()`\ .
    
    An Instance of this class represents the whole Engine, with all accompanying state and window/world objects.
    
    Be sure to keep your instance accessible, as it will be needed to create most other classes.
    """
    
    def __init__(self):
        self.window = None
        
        self.eventHandlers = {}
        
        self.cfg = config.Config({},defaults=config.DEFAULT_CONFIG)
        self.keybinds = keybind.KeybindHandler(self)
    
    def createWindow(self,cls=window.PengWindow,*args,**kwargs):
        """
        createWindow(cls=window.PengWindow, *args, **kwargs)
        
        Creates a new window using the supplied ``cls``\ .
        
        If ``cls`` is not given, :py:class:`peng3d.window.PengWindow()` will be used.
        
        Any other positional or keyword arguments are passed to the class constructor.
        
        Note that this method currently does not support using multiple windows.
        
        .. todo::
           
           Implement having multiple windows.
        """
        self.window = cls(self,*args,**kwargs)
    
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
