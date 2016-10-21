#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  widgets.py
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

__all__ = [
    "BasicWidget","Background",
    "Widget","EmptyBackground",
    ]

import time

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode

def mouse_aabb(mpos,size,pos):
    return pos[0]<=mpos[0]<=pos[0]+size[0] and pos[1]<=mpos[1]<=pos[1]+size[1]

class Background(object):
    def __init__(self,widget):
        self.widget = widget
    def init_bg(self):
        pass
    def redraw_bg(self):
        pass
    
    @property
    def submenu(self):
        return self.widget.submenu
    
    @property
    def window(self):
        return self.widget.window
    
    @property
    def peng(self):
        return self.widget.peng

class EmptyBackground(Background):
    pass

class BasicWidget(object):
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None):
        self.name = name
        self.submenu = submenu
        self.window = window
        self.peng = peng
        
        self.actions = {}
        
        self.vlists = []
        
        self._pos = pos
        self._size = size
        
        self.is_hovering = False
        self.pressed = False
        self._enabled = True
        
        self.registerEventHandlers()
    
    def registerEventHandlers(self):
        self.peng.registerEventHandler("on_mouse_press",self.on_mouse_press)
        self.peng.registerEventHandler("on_mouse_release",self.on_mouse_release)
        self.peng.registerEventHandler("on_mouse_drag",self.on_mouse_drag)
        self.peng.registerEventHandler("on_mouse_motion",self.on_mouse_motion)
        self.peng.registerEventHandler("on_resize",self.on_resize)
    
    @property
    def pos(self):
        if isinstance(self._pos,list) or isinstance(self._pos,tuple):
            return self._pos
        elif callable(self._pos):
            return self._pos(self.window.width,self.window.height,*self.size)
        else:
            raise TypeError("Invalid position type")
    
    @property
    def size(self):
        if isinstance(self._size,list) or isinstance(self._size,tuple):
            return self._size
        elif callable(self._size):
            return self._size(self.window.width,self.window.height)
        else:
            raise TypeError("Invalid size type")
    
    @property
    def clickable(self):
        return self.submenu.name == self.submenu.menu.activeSubMenu and self.submenu.menu.name == self.window.activeMenu and self.enabled
    @clickable.setter
    def clickable(self,value):
        self._enabled=value
        self.redraw()
    
    @property
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self,value):
        self._enabled=value
        self.redraw()
    
    def addAction(self,action,func,*args,**kwargs):
        if action not in self.actions:
            self.actions[action] = []
        self.actions[action].append((func,args,kwargs))
    def doAction(self,action):
        for f,args,kwargs in self.actions.get(action,[]):
            f(*args,**kwargs)
    
    def draw(self):
        for vlist,t in self.vlists:
            vlist.draw(t)
    def redraw(self):
        pass
    
    def on_mouse_press(self,x,y,button,modifiers):
        if not self.clickable:
            return
        elif mouse_aabb([x,y],self.size,self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("press")
                self.pressed = True
            elif button == pyglet.window.mouse.RIGHT:
                self.doAction("context")
            self.redraw()
    def on_mouse_release(self,x,y,button,modifiers):
        if not self.clickable:
            return
        if self.pressed:
            if mouse_aabb([x,y],self.size,self.pos):
                self.doAction("click")
            self.pressed = False
            self.redraw()
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        self.on_mouse_motion(x,y,dx,dy)
    def on_mouse_motion(self,x,y,dx,dy):
        if not self.clickable:
            return
        if mouse_aabb([x,y],self.size,self.pos):
            if not self.is_hovering:
                self.is_hovering = True
                self.doAction("hover_start")
                self.redraw()
            else:
                self.doAction("hover")
        else:
            if self.is_hovering:
                self.is_hovering = False
                self.doAction("hover_end")
                self.redraw()
    def on_resize(self,width,height):
        self.redraw()

class Widget(BasicWidget):
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None
                ):
        self.bg = bg
        self.bg_initialized = False
        super(Widget,self).__init__(name,submenu,window,peng,pos,size)
    def setBackground(self,bg):
        self.bg = bg
        self.redraw()
    
    def redraw(self):
        if self.bg is not None:
            if not self.bg_initialized:
                self.bg.init_bg()
                self.bg_initialized=True
            self.bg.redraw_bg()
        super(Widget,self).redraw()
