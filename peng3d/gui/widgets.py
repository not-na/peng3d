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

import weakref
import time

# Internal Debug/Performance monitor variable
_num_saved_redraws = 0

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode

from ..util import mouse_aabb, WatchingList as _WatchingList

class Background(object):
    """
    Class representing the background of a widget.
    
    This base class does not do anything.
    """
    def __init__(self,widget):
        self.widget = widget
        self.initialized = False
        self._vlists = []
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
    
    def reg_vlist(self,vlist):
        """
        Registers a vertex list to the internal list.
        
        This allows the class to clean itself up properly during deletion, as the background would still be visible after deletion otherwise.
        """
        self._vlists.append(vlist)
    
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
    
    @property
    def pressed(self):
        """
        Read-only helper property for easier access.
        
        Equivalent to ``widget.pressed``\ .
        """
        return self.widget.pressed
    @property
    def is_hovering(self):
        """
        Read-only helper property for easier access.
        
        Equivalent to ``widget.is_hovering``\ .
        """
        return self.widget.is_hovering
    
    def __del__(self):
        for vlist in self._vlists:
            try:
                vlist.delete()
            except Exception:
                pass
        self._vlists=[]

class EmptyBackground(Background):
    """
    Background that draws simply nothing.
    
    Can be used as a placeholder.
    """
    pass

class BasicWidget(object):
    """
    Basic Widget class.
    
    Every widget must be registered with their appropriate sub-menus to work properly.
    
    ``pos`` may be either a list or 2-tuple of ``(x,y)`` for static positions or a function with the signature ``window_width,window_height,widget_width,widget_height`` returning a tuple.
    
    ``size`` is similar to ``pos`` but will only get ``window_width,window_height`` as its arguments.
    
    Commonly, the lambda ``lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.)`` is used to center the widget.
    
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None):
        self.name = name
        self.submenu = submenu
        self.window = window
        self.peng = peng
        
        self.actions = {}
        
        self._pos = pos
        self._size = size
        
        self.is_hovering = False
        self.pressed = False
        self._enabled = True
        self._is_scrollbar = False
        self.do_redraw = True
        
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
        
        The returned object will actually be an instance of a helper class to allow for setting only the x/y coordinate.
        
        This property also respects any :py:class:`Container` set as its parent, any offset will be added automatically.
        
        Note that setting this property will override any callable set permanently.
        """
        if isinstance(self._pos,list) or isinstance(self._pos,tuple):
            r = self._pos
        elif callable(self._pos):
            w,h = self.submenu.size[:]
            r = self._pos(w,h,*self.size)
        else:
            raise TypeError("Invalid position type")
        
        ox,oy = self.submenu.pos
        r = r[0]+ox,r[1]+oy
        
        if isinstance(self.submenu,ScrollableContainer) and not self._is_scrollbar:# and self.name != "__scrollbar_%s"%self.submenu.name: # Widget inside scrollable container and not the scrollbar
            r = r[0],r[1]+self.submenu.offset_y
        return _WatchingList(r,self._wlredraw_pos)
    @pos.setter
    def pos(self,value):
        self._pos = value
        self.redraw()
    
    @property
    def size(self):
        """
        Similar to :py:attr:`pos` but for the size instead.
        """
        if isinstance(self._size,list) or isinstance(self._size,tuple):
            s = self._size
        elif callable(self._size):
            w,h = self.submenu.size[:]
            s = self._size(w,h)
        else:
            raise TypeError("Invalid size type")
        
        # Prevents crashes with negative size
        s = [max(s[0],0),max(s[1],0)]
        return _WatchingList(s,self._wlredraw_size)
    @size.setter
    def size(self,value):
        self._size = value
        self.redraw()
    
    @property
    def clickable(self):
        """
        Property used for determining if the widget should be clickable by the user.
        
        This is only true if the submenu of this widget is active and this widget is enabled.
        
        The widget may be either disabled by setting this property or the :py:attr:`enabled` attribute.
        """
        if not isinstance(self.submenu,Container):
            return self.submenu.name == self.submenu.menu.activeSubMenu and self.submenu.menu.name == self.window.activeMenu and self.enabled
        else:
            return self.submenu.clickable and self.enabled
    @clickable.setter
    def clickable(self,value):
        self._enabled=value
        self.redraw()
    
    @property
    def enabled(self):
        """
        Property used for storing whether or not this widget is enabled.
        
        May influence rendering and behavior.
        
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
        - ``hover`` is called every time the cursor moves while still being over the widget
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
    
    def getState(self):
        """
        Returns the current state of the widget.
        
        One of ``"pressed"``\ , ``"hover"``\ , ``"disabled"`` or ``"idle"``\ .
        Note that some information may be lost by getting this state, 
        for example it is not possible to know if the widget is hovered or not
        if ``"pressed"`` is returned. However, this should not be a problem for
        most intended uses of this method.
        """
        # Does not convey all information, loses some
        if self.pressed:
            return "pressed"
        elif self.is_hovering:
            return "hover"
        elif not self.enabled:
            return "disabled"
        else:
            return "idle"
    
    def draw(self):
        """
        Draws all vertex lists associated with this widget.
        """
        if self.do_redraw:
            self.on_redraw()
            self.do_redraw = False
    def redraw(self):
        """
        Triggers a redraw of the widget.
        
        Note that the redraw may not be executed instantly, but rather batched together on the next frame.
        If an instant and synchronous redraw is needed, use :py:meth:`on_redraw()` instead.
        """
        # Uncomment if you want to see how many unneccessary redraws have been prevented
        # Warning: may cause lots of console spam and thus inaccurate results
        #if self.do_redraw:
        #    # Debug - not for production use
        #    global _num_saved_redraws
        #    _num_saved_redraws+=1
        #    print("saved redraw #%s"%_num_saved_redraws)
        self.do_redraw = True
    def on_redraw(self):
        """
        Callback to be overridden by subclasses called if redrawing the widget seems necessary.
        
        Note that this method should not be called manually, see :py:meth:`redraw()` instead.
        """
        pass
    
    def _wlredraw_pos(self,wl):
        self._pos = wl[:]
        self.redraw()
    def _wlredraw_size(self,wl):
        self._size = wl[:]
        self.redraw()
    
    def on_mouse_press(self,x,y,button,modifiers):
        if not self.clickable:
            return
        elif mouse_aabb([x,y],self.size,self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("press")
                self.pressed = True
                self.doAction("statechanged")
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
            self.doAction("statechanged")
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
                self.doAction("statechanged")
                self.redraw()
            else:
                self.doAction("hover")
        else:
            if self.is_hovering:
                self.is_hovering = False
                self.doAction("hover_end")
                self.doAction("statechanged")
                self.redraw()
    def on_resize(self,width,height):
        self.redraw()
    
    def delete(self):
        """
        Deletes resources of this widget that require manual cleanup.
        
        Currently removes all actions, event handlers and the background.
        
        The background itself should automatically remove all vertex lists to avoid visual artifacts.
        
        Note that this method is currently experimental, as it seems to have a memory leak.
        """
        # TODO: fix memory leak upon widget deletion
        del self.bg.widget
        del self.bg
        
        #self.clickable=False
        
        del self._pos
        del self._size
        
        self.actions = {}
        
        for e_type,e_handlers in self.peng.eventHandlers.items():
            if True or e_type in eh:
                to_del = []
                for e_handler in e_handlers:
                    # Weird workaround due to implementation details of WeakMethod
                    if super(weakref.WeakMethod,e_handler).__call__() is self:
                        to_del.append(e_handler)
                for d in to_del:
                    try:
                        #print("Deleting handler %s of type %s"%(d,e_type))
                        del e_handlers[e_handlers.index(d)]
                    except Exception:
                        #print("Could not delete handler %s, memory leak may occur"%d)
                        import traceback;traceback.print_exc()
    #def __del__(self):
    #    print("del %s"%self.name)
    #    try:
    #        del self.bg
    #    except Exception:
    #        pass

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
        super(Widget,self).__init__(name,submenu,window,peng,pos,size)
    def setBackground(self,bg):
        """
        Sets the background of the widget.
        
        This may cause the background to be initialized.
        """
        self.bg = bg
        self.redraw()
    
    def on_redraw(self):
        """
        Draws the background and the widget itself.
        
        Subclasses should use ``super()`` to call this method, or rendering may glitch out.
        """
        if self.bg is not None:
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.initialized=True
            self.bg.redraw_bg()
        super(Widget,self).on_redraw()
