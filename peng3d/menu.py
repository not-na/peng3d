#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  menu.py
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

__all__ = ["BasicMenu","Menu"]

import weakref
import inspect

from .layer import Layer
from .util import ActionDispatcher

class BasicMenu(ActionDispatcher):
    """
    Menu base class without layer support.
    
    Each menu is separated from the other menus and can be switched between at any time.
    
    Actions supported by default:
    
    ``enter`` is triggered everytime the :py:meth:`on_enter()` method has been called.
    
    ``exit`` is triggered everytime the :py:meth:`on_exit()` method has been called.
    
    .. seealso::
       
       See :py:class:`Menu()` for more information.
    
    """
    
    def __init__(self,name,window,peng):
        self.name = name
        self.window = window
        self.peng = peng
        
        self.eventHandlers = {}
        
        self.worlds = []
    def draw(self):
        """
        This method is called if it is time to render the menu.
        
        Override this method in subclasses to customize behavior and actually draw stuff.
        """
        pass
    
    def addWorld(self,world):
        """
        Adds the given world to the internal list.
        
        Worlds that are registered via this method will get all events that are given to this menu passed through.
        
        This mechanic is mainly used to implement actor controllers.
        """
        self.worlds.append(world)
    
    # Event handlers
    def handleEvent(self,event_type,args):
        if event_type in self.eventHandlers:
            for whandler in self.eventHandlers[event_type]:
                # This allows for proper collection of deleted handler methods by using weak references
                handler = whandler()
                if handler is None:
                    del self.eventHandlers[event_type][self.eventHandlers[event_type].index(whandler)]
                handler(*args)
        for world in self.worlds:
            world.handle_event(event_type,args,self.window)
    handleEvent.__noautodoc__ = True
    def registerEventHandler(self,event_type,handler):
        if event_type not in self.eventHandlers:
            self.eventHandlers[event_type]=[]
        # Only a weak reference is kept
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        else:
            handler = weakref.ref(handler)
        self.eventHandlers[event_type].append(handler)
    
    def on_enter(self,old):
        """
        This fake event handler will be called every time this menu is entered via the :py:meth:`PengWindow.changeMenu()` method.
        
        This handler will not be called if this menu is already active.
        """
        pass # Custom fake event handler for entering the menu
    def on_exit(self,new):
        """
        This fake event handler will be called every time this menu is exited via the :py:meth:`PengWindow.changeMenu()` method.
        
        This handler will not be called if this menu is the same as the new menu.
        """
        pass # Custom fake event handler for leaving the menu

class Menu(BasicMenu):
    """
    Subclass of :py:class:`BasicMenu` adding support for the :py:class:`Layer` class.
    
    This subclass overrides the draw and __init__ method, so be sure to call them if you override them.
    """
    
    def __init__(self,name,window,peng):
        super(Menu,self).__init__(name,window,peng)
        self.layers = []
    def addLayer(self,layer,z=-1):
        """
        Adds a new layer to the stack, optionally at the specified z-value.
        
        ``layer`` must be an instance of Layer or subclasses.
        
        ``z`` can be used to override the index of the layer in the stack. Defaults to ``-1`` for appending.
        """
        # Adds a new layer to the stack, optionally at the specified z-value
        # The z-value is the index this layer should be inserted in, or -1 for appending
        if not isinstance(layer,Layer):
            raise TypeError("layer must be an instance of Layer!")
        if z==-1:
            self.layers.append(layer)
        else:
            self.layers.insert(z,layer)
    def draw(self):
        """
        Draws the layers in the appropriate order.
        
        Layers that have their ``enabled`` attribute set to ``False`` are skipped.
        """
        # Draws each layer in the given order
        for layer in self.layers:
            if layer.enabled:
                layer._draw()
    
    def on_enter(self,old):
        """
        Same as :py:meth:`BasicMenu.on_enter()`\\ , but also calls :py:meth:`Layer.on_menu_enter()` on every layer.
        """
        for layer in self.layers:
            layer.on_menu_enter(old)
    def on_exit(self,new):
        """
        Same as :py:meth:`BasicMenu.on_exit()`\\ , but also calls :py:meth:`Layer.on_menu_exit()` on every layer.
        """
        for layer in self.layers:
            layer.on_menu_exit(new)
    
