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

__all__ = ["GUIMenu","SubMenu","GUILayer"]

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode

from ..menu import Menu
from ..layer import Layer,Layer2D
from .widgets import *
from .button import *
from .slider import *

class GUIMenu(Menu):
    """
    :py:class:`peng3d.menu.Menu` subclass adding 2D GUI Support.
    
    Note that widgets are not managed directly by this class, but rather by each :py:class:`SubMenu`\ .
    """
    def __init__(self,name,window,peng):
        super(GUIMenu,self).__init__(name,window,peng)
        pyglet.clock.schedule_interval(lambda dt: None,1./30)
        self.submenus = {}
        self.activeSubMenu = None
    
    def addSubMenu(self,submenu):
        """
        Adds a :py:class:`SubMenu` to this Menu.
        
        Note that nothing will be displayed unless a submenu is activated.
        """
        self.submenus[submenu.name] = submenu
    def changeSubMenu(self,submenu):
        """
        Changes the submenu that is displayed.
        
        :raises ValueError: if the name was not previously registered
        """
        if submenu not in self.submenus:
            raise ValueError("Submenu %s does not exist!"%submenu)
        elif submenu == self.activeSubMenu:
            return # Ignore double submenu activation to prevent bugs in submenu initializer
        old = self.activeSubMenu
        self.activeSubMenu = submenu
        if old is not None:
            self.submenus[old].on_exit(submenu)
        self.submenu.on_enter(old)
    
    def draw(self):
        """
        Draws each menu layer and the active submenu.
        
        Note that the layers are drawn first and may be overriden by the submenu and widgets.
        """
        super(GUIMenu,self).draw()
        self.submenu.draw()
    
    @property
    def submenu(self):
        """
        Property containing the :py:class:`SubMenu` instance that is currently active.
        """
        return self.submenus[self.activeSubMenu]

class SubMenu(object):
    """
    Sub Menu of the GUI system.
    
    Each instance must be registered with their menu to work properly, see :py:meth:`GUIMenu.addSubMenu()`\ .
    """
    def __init__(self,name,menu,window,peng):
        self.name = name
        self.menu = menu
        self.window = window
        self.peng = peng
        
        self.widgets = {}
        
        self.bg = [242,241,240,255]
        self.bg_vlist = pyglet.graphics.vertex_list(4,
            "v2f",
            "c4B",
            )
        self.peng.registerEventHandler("on_resize",self.on_resize)
        self.on_resize(self.window.width,self.window.height)
        
        self.batch2d = pyglet.graphics.Batch()
    
    def draw(self):
        """
        Draws the submenu and its background.
        
        Note that this leaves the OpenGL state set to 2d drawing.
        """
        self.window.set2d()
        if isinstance(self.bg,Layer):
            self.bg._draw()
        elif hasattr(self.bg,"draw") and callable(self.bg.draw):
            self.bg.draw()
        elif isinstance(self.bg,list) or isinstance(self.bg,tuple):
            self.bg_vlist.draw(GL_QUADS)
        elif callable(self.bg):
            self.bg()
        elif self.bg=="blank":
            pass
        else:
            raise TypeError("Unknown background type")
        self.window.set2d() # In case the bg layer was in 3d
        self.batch2d.draw()
        for widget in self.widgets.values():
            widget.draw()
    
    def addWidget(self,widget):
        """
        Adds a widget to this submenu.
        """
        self.widgets[widget.name]=widget
    def getWidget(self,name):
        """
        Returns the widget with the given name.
        """
        return self.widgets[name]
    
    def setBackground(self,bg):
        """
        Sets the background of the submenu.
        
        The background may be a RGB or RGBA color to fill the background with.
        
        Alternatively, a :py:class:`peng3d.layer.Layer` instance or other object with a ``.draw()`` method may be supplied.
        It is also possible to supply any other method or function that will get called.
        
        Lastly, the string ``"blank"`` may be passed to skip background drawing.
        """
        self.bg = bg
        if isinstance(bg,list) or isinstance(bg,tuple):
            if len(bg)==3 and isinstance(bg,list):
                bg.append(255)
            self.bg_vlist.colors = bg*4
    
    def on_resize(self,width,height):
        sx,sy = width,height
        self.bg_vlist.vertices = [0,0, sx,0, sx,sy, 0,sy]
    
    def on_enter(self,old):
        pass
    def on_exit(self,new):
        pass

class GUILayer(GUIMenu,Layer2D):
    """
    Hybrid of :py:class:`GUIMenu` and :py:class:`peng3d.layer.Layer2D`\ .
    
    This class allows you to create Head-Up Displays and other overlays easily.
    """
    # TODO: add safety recursion breaker if this is added as a layer to itself
    def __init__(self,name,menu,window,peng):
        Layer2D.__init__(self,menu,window,peng)
        GUIMenu.__init__(self,menu.name,window,peng)
    def draw(self):
        """
        Draws the Menu.
        """
        self.predraw()
        GUIMenu.draw(self)
        self.postdraw()
