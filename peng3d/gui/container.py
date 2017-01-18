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

__all__ = ["Container", "ScrollableContainer", "ContainerButtonBackground"]

import collections

import pyglet
from pyglet.gl import *

from .widgets import Widget, Background, _WatchingList
from .slider import VerticalSlider
from .button import ButtonBackground
from ..layer import Layer

class ContainerButtonBackground(ButtonBackground):
    """
    Background class used to render the background of containers using a button style.
    
    Mostly identical with :py:class:`ButtonBackground` with added compatibility for containers.
    """
    def init_bg(self):
        self.vlist = self.widget.batch2d.add(20,GL_QUADS,None,
            "v2f",
            "c3B",
            )
    def redraw_bg(self):
        # Convenience variables
        sx,sy = self.widget.size
        x,y = self.widget.pos
        bx,by = self.border
        
        # Button background
        
        # Outer vertices
        #    x          y
        v1 = x,         y+sy
        v2 = x+sx,      y+sy
        v3 = x,         y
        v4 = x+sx,      y
        
        # Inner vertices
        #    x          y
        v5 = x+bx,      y+sy-by
        v6 = x+sx-bx,   y+sy-by
        v7 = x+bx,      y+by
        v8 = x+sx-bx,   y+by
        
        # 5 Quads, for edges and the center
        qb1 = v5+v6+v2+v1
        qb2 = v8+v4+v2+v6
        qb3 = v3+v4+v8+v7
        qb4 = v3+v7+v5+v1
        qc  = v7+v8+v6+v5
        
        v = qb1+qb2+qb3+qb4+qc
        
        self.vlist.vertices = v
        
        bg = self.submenu.bg[:3] if isinstance(self.submenu.bg,list) or isinstance(self.submenu.bg,tuple) else [242,241,240]
        o,i = bg, [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]
        s,h = [max(bg[0]-40,0),max(bg[1]-40,0),max(bg[2]-40,0)], [min(bg[0]+12,255),min(bg[1]+12,255),min(bg[2]+12,255)]
        # Outer,Inner,Shadow,Highlight
        
        i = bg
        
        if self.borderstyle == "flat":
            # Flat style makes no difference between normal,hover and pressed
            cb1 = i+i+i+i
            cb2 = i+i+i+i
            cb3 = i+i+i+i
            cb4 = i+i+i+i
            cc  = i+i+i+i
        elif self.borderstyle == "gradient":
            cb1 = i+i+o+o
            cb2 = i+o+o+i
            cb3 = o+o+i+i
            cb4 = o+i+i+o
            cc  = i+i+i+i
        elif self.borderstyle == "oldshadow":
            # Flipped from default
            cb1 = s+s+s+s
            cb2 = h+h+h+h
            cb3 = h+h+h+h
            cb4 = s+s+s+s
            cc  = i+i+i+i
        elif self.borderstyle == "material":
            cb1 = s+s+o+o
            cb2 = s+o+o+s
            cb3 = o+o+s+s
            cb4 = o+s+s+o
            cc  = i+i+i+i
        else:
            raise ValueError("Invalid Border style")
        
        c = cb1+cb2+cb3+cb4+cc
        
        self.vlist.colors = c

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
        
        self.widgets = collections.OrderedDict()
        
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
        elif bg in ["flat","gradient","oldshadow","material"]:
            self.bg = ContainerButtonBackground(self,borderstyle=bg)
            self.redraw()
    
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
        # TODO: Remove old stencil code completely in future version
        #if not isinstance(self.submenu,Container):
        #    # Stencil setup
        #    glClear(GL_STENCIL_BUFFER_BIT)
        #    glEnable(GL_STENCIL_TEST)
        #    
        #    # Set up the stencil for this container
        #    glStencilFunc(GL_ALWAYS,1,0xFF)
        #    glStencilOp(GL_KEEP,GL_KEEP,GL_REPLACE)
        #    glStencilMask(0xFF)
        #    
        #    # Practically hides most drawing operations, should be redundant since the quad is fully transparent
        #    glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        #    glDepthMask(GL_FALSE)
        #    
        #    self.stencil_vlist.draw(GL_QUADS)
        #    
        #    # Reset to proper state and set up the stencil func/mask
        #    glStencilFunc(GL_EQUAL,1,0xFF)
        #    glStencilMask(0x00)
        #    glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        #    glDepthMask(GL_TRUE)
        if not isinstance(self.submenu,Container):
            # Much easier and probably faster than stenciling
            glEnable(GL_SCISSOR_TEST)
            glScissor(*self.pos+self.size)
        
        # Stenciled code
        SubMenu.draw(self)
        
        #if not isinstance(self.submenu,Container):
        #    # Stencil teardown
        #    glDisable(GL_STENCIL_TEST)
        #    # Make sure to disable the stencil test first, or the stencil buffer will only clear areas that are allowed to by glStencilFunc
        #    glClear(GL_STENCIL_BUFFER_BIT)
        if not isinstance(self.submenu,Container):
            glDisable(GL_SCISSOR_TEST)
    
    def redraw(self):
        """
        Redraws the background and any child widgets.
        """
        x,y = self.pos
        sx,sy = self.size
        self.bg_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
        self.stencil_vlist.vertices = [x,y, x+sx,y, x+sx,y+sy, x,y+sy]
        if isinstance(self.bg,Background):
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.initialized=True
            self.bg.redraw_bg()
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
