#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  container.py
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

__all__ = ["Container", "ScrollableContainer"]

import pyglet
from pyglet.gl import *

from .widgets import Widget, _WatchingList
from .slider import VerticalSlider
from ..layer import Layer

class Container(Widget):
    """
    Main class of the container system.
    
    This widget may contain other widgets, limiting the childs to only draw within the defined bounds.
    Additionally, the given position will also act as a offset, making the child coordinates relative to the parent.
    
    This Class is a subclass of :py:class:`peng3d.gui.widgets.Widget` but also exhibits part of the API of :py:class:`peng3d.gui.SubMenu`\ .
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                ):
        super(Container,self).__init__(name,submenu,window,peng,pos,size)
        
        self.menu = submenu
        
        self.widgets = {}
        
        self.bg = [242,241,240,255]
        self.bg_vlist = pyglet.graphics.vertex_list(4,
            "v2f",
            "c4B",
            )
        self.stencil_vlist = pyglet.graphics.vertex_list(4,
            "v2f",
            ("c4B",[0,0,0,0]*4),
            )
        self.peng.registerEventHandler("on_resize",self.on_resize)
        self.on_resize(self.window.width,self.window.height)
        
        self.batch2d = pyglet.graphics.Batch()
        
    def setBackground(self,bg):
        """
        Sets the background of the Container.
        
        Similar to :py:meth:`peng3d.gui.SubMenu.setBackground()`\ , but only effects the region covered by the Container.
        """
        self.bg = bg
        if isinstance(bg,list) or isinstance(bg,tuple):
            if len(bg)==3 and isinstance(bg,list):
                bg.append(255)
            self.bg_vlist.colors = bg*4
    
    def on_resize(self,width,height):
        x,y = self.pos
        sx,sy = self.size
        self.bg_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
        self.stencil_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
    
    def addWidget(self,widget):
        """
        Adds a widget to this container.
        
        Note that trying to add the Container to itself will be ignored.
        """
        if self is widget: # Prevents being able to add the container to itself, causing a recursion loop on redraw
            return
        self.widgets[widget.name]=widget
    def getWidget(self,name):
        """
        Returns the widget with the given name.
        """
        return self.widgets[name]
    
    def draw(self):
        """
        Draws the submenu and its background.
        
        Note that this leaves the OpenGL state set to 2d drawing and may modify the stencil settings and buffer.
        """
        
        # Stencil setup
        glEnable(GL_STENCIL_TEST)
        #mask = pyglet.image.get_buffer_manager().get_buffer_mask()
        #glSetAttribute(GL_STENCIL_SIZE,8)
        
        # Set up the stencil for this container
        glStencilFunc(GL_ALWAYS,1,0xFF)
        glStencilOp(GL_KEEP,GL_KEEP,GL_REPLACE)
        glStencilMask(0xFF)
        glClear(GL_STENCIL_BUFFER_BIT)
        
        # Practically hides most drawing operations, should be redundant since the quad is fully transparent
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        glDepthMask(GL_FALSE)
        
        self.stencil_vlist.draw(GL_QUADS)
        
        # Reset to proper state and set up the stencil func/mask
        glStencilFunc(GL_EQUAL,1,0xFF)
        glStencilMask(0x00)
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        glDepthMask(GL_TRUE)
        
        # Stenciled code
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
        glStencilFunc(GL_EQUAL,1,0xFF)
        glStencilMask(0x00)
        self.batch2d.draw()
        for widget in self.widgets.values():
            widget.draw()
        
        # Stencil teardown
        glDisable(GL_STENCIL_TEST)
        # Make sure to disable the stencil test first, or the stencil buffer will only clear areas that are allowed to by glStencilFunc
        glClear(GL_STENCIL_BUFFER_BIT)
    
    def redraw(self):
        """
        Redraws the background and any child widgets.
        """
        x,y = self.pos
        sx,sy = self.size
        self.bg_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
        self.stencil_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
        for widget in self.widgets.values():
            widget.redraw()
    
    def on_enter(self,old):
        """
        Dummy method defined for compatibility with :py:class:`peng3d.gui.SubMenu`, simply does nothing.
        """
        pass
    def on_exit(self,new):
        """
        Dummy method defined for compatibility with :py:class:`peng3d.gui.SubMenu`, simply does nothing.
        """
        pass

class ScrollableContainer(Container):
    """
    Subclass of :py:class:`Container` allowing for scrolling its content.
    
    The scrollbar currently is always on the right side and simply consists of a :py:class:`peng3d.gui.slider.VerticalSlider`\ .
    
    ``scrollbar_width`` and ``borderstyle`` will be passed to the scrollbar.
    
    ``content_height`` refers to the maximum offset the user can scroll to.
    
    The content height may be changed, but manually calling :py:meth:`redraw()` will be necessary.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 scrollbar_width=12,
                 borderstyle="flat",
                 content_height=100,
                ):
        self.offset_y = 0
        self.content_height = content_height
        super(ScrollableContainer,self).__init__(name,submenu,window,peng,pos,size)
        self._scrollbar = VerticalSlider("__scrollbar_%s"%name,self,self.peng.window,self.peng,
                                pos=[0,0],
                                size=[24,0],
                                borderstyle=borderstyle,
                                border=[3,3],
                                n=self.content_height,
                                nmax=self.content_height,
                                )
        self._scrollbar._is_scrollbar = True
        self._scrollbar.addAction("progresschange",self.redraw)
        self.addWidget(self._scrollbar)
        
        self.redraw()
    
    def redraw(self):
        """
        Redraws the background and contents, including scrollbar.
        
        This method will also check the scrollbar for any movement and will be automatically called on movement of the slider.
        """
        n = self._scrollbar.n
        self.offset_y = -n # Causes the content to move in the opposite direction of the slider
        
        # Size of scrollbar
        sx=24 # Currently constant, TODO: add dynamic sx of scrollbar
        sy=self.size[1]
        # Pos of scrollbar
        x=self.size[0]-sx
        y=0 # Currently constant, TODO: add dynamic y-pos of scrollbar
        
        # Dynamic pos/size may be added via align/lambda/etc.
        
        # Note that the values are written to the _* variant of the attribute to avoid 3 uneccessary redraws
        self._scrollbar._size = sx,sy
        self._scrollbar._pos = x,y
        self._scrollbar._nmax = self.content_height
        
        super(ScrollableContainer,self).redraw() # Re-draws everything, including child widgets


# Hack to allow BasicWidget to do isinstance of Container/ScrollableContainer for offset code
from ..gui import widgets
widgets.Container = Container
widgets.ScrollableContainer = ScrollableContainer
