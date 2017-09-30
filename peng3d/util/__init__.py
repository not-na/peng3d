#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#  
#  Copyright 2017 notna <notna@apparat.org>
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

import weakref

from .gui import *

class WatchingList(list):
    """
    Subclass of :py:func:`list` implementing a watched list.
    
    A WatchingList will call the given callback with a reference to itself whenever it is modified.
    Internally, the callback is stored as a weak reference, meaning that the creator should keep a reference around.
    
    This class is used in :py:class:`peng3d.gui.widgets.BasicWidget()` to allow for modifying single coordinates of the pos and size properties.
    """
    def __init__(self,l,callback=lambda:None):
        self.callback = weakref.WeakMethod(callback)
        super(WatchingList,self).__init__(l)
    def __setitem__(self,*args):
        super(WatchingList,self).__setitem__(*args)
        c = self.callback()(self)

def register_pyglet_handler(peng,func,event,raiseErrors=False):
    peng.addEventListener("pyglet:%s"%event,(lambda data:func(*data["args"])),raiseErrors)

class ActionDispatcher(object):
    def addAction(self,action,func,*args,**kwargs):
        """
        Adds a callback to the specified action.
        
        All other positional and keyword arguments will be stored and passed to the function upon activation.
        """
        if not hasattr(self,"actions"):
            self.actions = {}
        if action not in self.actions:
            self.actions[action] = []
        self.actions[action].append((func,args,kwargs))
    def doAction(self,action):
        """
        Helper method that calls all callbacks registered for the given action.
        """
        if not hasattr(self,"actions"):
            return
        for f,args,kwargs in self.actions.get(action,[]):
            f(*args,**kwargs)
