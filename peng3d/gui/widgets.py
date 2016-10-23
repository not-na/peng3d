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
    "mouse_aabb",
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
    """
    Simple AABB collision algorithm used for checking if a mouse click hit a widget.
    """
    return pos[0]<=mpos[0]<=pos[0]+size[0] and pos[1]<=mpos[1]<=pos[1]+size[1]

class Background(object):
    """
    Class representing the background of a widget.
    
    This base class does not do anything.
    """
    def __init__(self,widget):
        self.widget = widget
    def init_bg(self):
        """
        Called just before the background will be drawn the first time.
        
        Commonly used to initialize vertex lists.
        
        It is recommended to add all vertex lists to the ``submenu.batch2d`` Batch to speed up rendering and preventing glitches with grouping.
        """
        pass
    def redraw_bg(self):
        """
        Method called by the parent widget every time its :py:meth:`Widget.redraw()` method is called.
        """
        pass
    
    @property
    def submenu(self):
        """
        Property for accessing the parent widget's submenu.
        """
        return self.widget.submenu
    
    @property
    def window(self):
        """
        Property for accessing the parent widget's window.
        """
        return self.widget.window
    
    @property
    def peng(self):
        """
        Property for accessing the parent widget's instance of :py:class:`peng3d.peng.Peng`\ .
        """
        return self.widget.peng

class EmptyBackground(Background):
    """
    Background that draws simply nothing.
    
    Can be used as a placeholder.
    """
    pass

class BasicWidget(object):
    """
    Basic Widget class.
    
    Every widget must be registered with their appropriate submenus to work properly.
    
    ``pos`` may be either a list or 2-tuple of ``(x,y)`` for static positions or a function with the signature ``window_width,window_height,widget_width,widget_height`` returning a tuple.
    
    ``size`` is similiar to ``pos`` but will only get ``window_width,window_height`` as its arguments.
    
    Commonly, the lambda ``lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.)`` is used to center the widget.
    
    """
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
        """
        Registers event handlers used by this widget, e.g. mouse click/motion and window resize.
        
        This will allow the widget to redraw itself upon resizing of the window in case the position needs to be adjusted.
        """
        self.peng.registerEventHandler("on_mouse_press",self.on_mouse_press)
        self.peng.registerEventHandler("on_mouse_release",self.on_mouse_release)
        self.peng.registerEventHandler("on_mouse_drag",self.on_mouse_drag)
        self.peng.registerEventHandler("on_mouse_motion",self.on_mouse_motion)
        self.peng.registerEventHandler("on_resize",self.on_resize)
    
    @property
    def pos(self):
        """
        Property that will always be a 2-tuple representing the position of the widget.
        
        Note that this method may call the method given as ``pos`` in the initializer.
        """
        if isinstance(self._pos,list) or isinstance(self._pos,tuple):
            return self._pos
        elif callable(self._pos):
            return self._pos(self.window.width,self.window.height,*self.size)
        else:
            raise TypeError("Invalid position type")
    
    @property
    def size(self):
        """
        Similiar to :py:attr:`pos` but for the size instead.
        """
        if isinstance(self._size,list) or isinstance(self._size,tuple):
            return self._size
        elif callable(self._size):
            return self._size(self.window.width,self.window.height)
        else:
            raise TypeError("Invalid size type")
    
    @property
    def clickable(self):
        """
        Property used for determining if the widget should be clickable by the user.
        
        This is only true if the submenu of this widget is active and this widget is enabled.
        
        The widget may be either disabled by setting this property or the :py:attr:`enabled` attribute.
        """
        return self.submenu.name == self.submenu.menu.activeSubMenu and self.submenu.menu.name == self.window.activeMenu and self.enabled
    @clickable.setter
    def clickable(self,value):
        self._enabled=value
        self.redraw()
    
    @property
    def enabled(self):
        """
        Property used for storing whether or not this widget is enabled.
        
        May influence rendering and behaviour.
        
        Note that the widget will be immediately redrawn if this property is changed.
        """
        return self._enabled
    @enabled.setter
    def enabled(self,value):
        self._enabled=value
        self.redraw()
    
    def addAction(self,action,func,*args,**kwargs):
        """
        Adds the a callback to the specified action.
        
        All other positional and keyword arguments will be stored and passed to the function upon activation.
        
        The actions available may differ from widget to widget, by default these are used:
        
        - ``press`` is called upon starting to click on the widget
        - ``click`` is called if the mouse is released on the widget while also having been pressed on it before, recommended for typical button callbacks
        - ``context`` is called upon right-clicking on the widget and may be used to display a context menu
        - ``hover_start`` signals that the cursor is now hovering over the widget
        - ``hover`` is called everytime the cursor moves while still being over the widget
        - ``hover_end`` is called after the cursor leaves the widget
        """
        if action not in self.actions:
            self.actions[action] = []
        self.actions[action].append((func,args,kwargs))
    def doAction(self,action):
        """
        Helper method that calls all callbacks registered for the given action.
        """
        for f,args,kwargs in self.actions.get(action,[]):
            f(*args,**kwargs)
    
    def draw(self):
        """
        Draws all vertex lists associated with this widget.
        
        :deprecated: Add vertex lists to the submenu instead
        """
        for vlist,t in self.vlists:
            vlist.draw(t)
    def redraw(self):
        """
        Callback to be overriden by subclasses called if redrawing the widget seems necessary.
        """
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
    """
    Subclass of :py:class:`BasicWidget` adding support for changing the :py:class:`Background`\ .
    
    If no background is given, an :py:class:`EmptyBackground` will be used instead.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None
                ):
        if bg is None:
            bg = EmptyBackground(self)
        self.bg = bg
        self.bg_initialized = False
        super(Widget,self).__init__(name,submenu,window,peng,pos,size)
    def setBackground(self,bg):
        """
        Sets the background of the widget.
        
        This may cause the background to be initialized.
        """
        self.bg = bg
        self.redraw()
    
    def redraw(self):
        """
        Draws the background and the widget itself.
        
        Subclasses should use ``super()`` to call this method, or rendering may glitch out.
        """
        if self.bg is not None:
            if not self.bg_initialized:
                self.bg.init_bg()
                self.bg_initialized=True
            self.bg.redraw_bg()
        super(Widget,self).redraw()
