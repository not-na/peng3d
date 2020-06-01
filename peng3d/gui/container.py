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
    change_on_press = False
    
    def getColors(self):
        bg,o,i,s,h = super(ContainerButtonBackground,self).getColors()
        i = bg
        
        return bg,o,i,s,h
    getColors.__noautodoc__ = getColors
    
    def bs_oldshadow(self,bg,o,i,s,h):
        if self.change_on_press and self.widget.pressed:
            i = s
            s,h = h,s
        elif self.change_on_press and self.widget.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
        cb1 = s+s+s+s
        cb2 = h+h+h+h
        cb3 = h+h+h+h
        cb4 = s+s+s+s
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    bs_oldshadow.__noautodoc__ = getColors

class Container(Widget):
    """
    Main class of the container system.
    
    This widget may contain other widgets, limiting the childs to only draw within the defined bounds.
    Additionally, the given position will also act as a offset, making the child coordinates relative to the parent.
    
    The :py:attr:`visible` attribute may be set to control whether or not this container is visible.
    
    This Class is a subclass of :py:class:`peng3d.gui.widgets.Widget` but also exhibits part of the API of :py:class:`peng3d.gui.SubMenu`\ .
    """

    IS_CLICKABLE = True
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,_skip_draw=False,
                 font=None, font_size=None,
                 font_color=None,
                 borderstyle=None,
                ):
        self.borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle
        self.font = font if font is not None else submenu.font
        self.font_size = font_size if font_size is not None else submenu.font_size
        self.font_color = font_color if font_color is not None else submenu.font_color
        super(Container,self).__init__(name,submenu,window,peng,pos,size)
        
        self.menu = submenu
        
        self.widgets = collections.OrderedDict()

        self.widget_order = {}
        
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
        if not _skip_draw:
            self.on_resize(*self.submenu.size)
        
        self.batch2d = pyglet.graphics.Batch()
        
        self.visible = True
        
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
            self.bg = ContainerButtonBackground(self,borderstyle=bg,batch=self.batch2d)
            self.redraw()
    
    def on_resize(self,width,height):
        # Stencil/BG Vlist are updated by redraw()
        self.redraw()
    
    @property
    def clickable(self):
        if not isinstance(self.submenu,Container):
            return self.submenu.name == self.submenu.menu.activeSubMenu and self.submenu.menu.name == self.window.activeMenu and self.enabled and self.visible
        else:
            return self.submenu.clickable and self.enabled and self.visible
    @clickable.setter
    def clickable(self,value):
        self._enabled=value
        self.redraw()
    
    def addWidget(self,widget, order_key=0):
        """
        Adds a widget to this container.
        
        Note that trying to add the Container to itself will be ignored.
        """
        if self is widget: # Prevents being able to add the container to itself, causing a recursion loop on redraw
            return
        self.widgets[widget.name]=widget

        if order_key not in self.widget_order:
            self.widget_order[order_key] = []
        self.widget_order[order_key].append(widget)
    def getWidget(self,name):
        """
        Returns the widget with the given name.
        """
        return self.widgets[name]
    
    def draw(self):
        """
        Draws the submenu and its background.
        
        Note that this leaves the OpenGL state set to 2d drawing and may modify the scissor settings.
        """
        if not self.visible:
            # Simple visibility check, has to be tested to see if it works properly
            return
        
        if not isinstance(self.submenu,Container):
            glEnable(GL_SCISSOR_TEST)
            glScissor(*[int(i) for i in self.pos+self.size])
        
        SubMenu.draw(self)
        
        if not isinstance(self.submenu,Container):
            glDisable(GL_SCISSOR_TEST)
    
    def on_redraw(self):
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
    
    def redraw(self):
        super(Container,self).redraw()
        
        # Also schedules redraws for sub-widgets
        for widget in self.widgets.values():
            widget.redraw()
    redraw.__noautodoc__ = True
    
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
                 font=None, font_size=None,
                 font_color=None,
                 borderstyle=None,
                 content_height=100,
                ):
        self.offset_y = 0
        self.content_height = content_height
        super(ScrollableContainer,self).__init__(name,submenu,window,peng,pos,size,borderstyle=borderstyle,
                                                 font=font, font_size=font_size, font_color=font_color,
                                                 _skip_draw=True,
                                                 )
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

        self.peng.registerEventHandler("on_mouse_scroll", self.on_mouse_scroll)
    
    def on_redraw(self):
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
        
        super(ScrollableContainer,self).on_redraw() # Re-draws everything, including child widgets

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.is_hovering:
            return

        dx = scroll_x * self.window.cfg["controls.scroll.mult_x"]
        dy = scroll_y * self.window.cfg["controls.scroll.mult_y"]

        # TODO: implement x-scrolling
        self._scrollbar.n += dy


# Hack to allow BasicWidget to do isinstance of Container/ScrollableContainer for offset code
from ..gui import widgets
widgets.Container = Container
widgets.ScrollableContainer = ScrollableContainer
