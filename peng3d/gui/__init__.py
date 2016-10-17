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

__all__ = ["GUIMenu","SubMenu"]

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode

from ..menu import Menu
from ..layer import Layer,Layer2D
from .widgets import *

class GUIMenu(Menu):
    def __init__(self,name,window,peng):
        super(GUIMenu,self).__init__(name,window,peng)
        pyglet.clock.schedule_interval(lambda dt: None,1./30)
        self.submenus = {}
        self.activeSubMenu = None
    
    def addSubMenu(self,submenu):
        self.submenus[submenu.name] = submenu
    def changeSubMenu(self,submenu):
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
        super(GUIMenu,self).draw()
        self.submenu.draw()
    
    @property
    def submenu(self):
        return self.submenus[self.activeSubMenu]

class SubMenu(object):
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
        for widget in self.widgets.values():
            widget.draw()
    
    def addWidget(self,widget):
        self.widgets[widget.name]=widget
    def getWidget(self,name):
        return self.widgets[name]
    
    def setBackground(self,bg):
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
    # TODO: add safety recursion breaker if this is added as a layer to itself
    def __init__(self,name,menu,window,peng):
        Layer2D.__init__(self,menu,window,peng)
        GUIMenu.__init__(self,menu.name,window,peng)
    def draw(self):
        self.predraw()
        GUIMenu.draw(self)
        self.postdraw()
