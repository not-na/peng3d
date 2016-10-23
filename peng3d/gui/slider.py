#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  slider.py
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
    "Progressbar","ProgressbarBackground",
    "Slider","SliderBackground",
]

import pyglet
from pyglet.gl import *

from .widgets import Background,Widget
from .button import ButtonBackground

class ProgressbarBackground(Background):
    """
    Background for the :py:class:`Progressbar` Widget.
    
    This background displays a bar with a border similiar to :py:class:`ButtonBackground`\ .
    Note that two colors may be given, one for the left and one for the right.
    """
    def __init__(self,widget,border,borderstyle,colors):
        super(ProgressbarBackground,self).__init__(widget)
        self.border = border
        self.borderstyle = borderstyle
        self.colors = colors
    def init_bg(self):
        self.vlist = self.submenu.batch2d.add(24,GL_QUADS,None,
            "v2f",
            "c3B",
            )
    def redraw_bg(self):
        x,y = self.widget.pos
        sx,sy = self.widget.size
        bx,by = self.border
        
        nmin,nmax,n = self.widget.nmin,self.widget.nmax,float(self.widget.n)
        p = min((n-nmin)/(nmax-nmin),1.)
        
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

        v9 = x+(sx-bx)*p,y+by
        v10= x+(sx-bx)*p,y+sy-by
        if p<=0:
            v9,v10=v7,v5
        
        # 5 Quads, for edges and the center
        qb1 = v5+v6+v2+v1
        qb2 = v8+v4+v2+v6
        qb3 = v3+v4+v8+v7
        qb4 = v3+v7+v5+v1
        qc1 = v7+v8+v6+v5
        qc2 = v7+v9+v10+v5
        
        v = qb1+qb2+qb3+qb4+qc1+qc2
        
        self.vlist.vertices = v
        
        bg = self.submenu.bg[:3] if isinstance(self.submenu.bg,list) or isinstance(self.submenu.bg,tuple) else [242,241,240]
        o,i = bg, [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]
        s,h = [max(bg[0]-40,0),max(bg[1]-40,0),max(bg[2]-40,0)], [min(bg[0]+12,255),min(bg[1]+12,255),min(bg[2]+12,255)]
        # Outer,Inner,Shadow,Highlight
        j,k = self.colors # Other progress color
        
        if self.borderstyle == "flat":
            # Flat style makes no difference between normal,hover and pressed
            cb1 = i+i+i+i
            cb2 = i+i+i+i
            cb3 = i+i+i+i
            cb4 = i+i+i+i
            cc1 = i+i+i+i
            cc2 = j+k+k+j
        elif self.borderstyle == "gradient":
            cb1 = i+i+o+o
            cb2 = i+o+o+i
            cb3 = o+o+i+i
            cb4 = o+i+i+o
            cc1 = i+i+i+i
            cc2 = j+k+k+j
        elif self.borderstyle == "oldshadow":
            cb1 = h+h+h+h
            cb2 = s+s+s+s
            cb3 = s+s+s+s
            cb4 = h+h+h+h
            cc1 = i+i+i+i
            cc2 = j+k+k+j
        elif self.borderstyle == "material":
            cb1 = s+s+o+o
            cb2 = s+o+o+s
            cb3 = o+o+s+s
            cb4 = o+s+s+o
            cc1 = i+i+i+i
            cc2 = j+k+k+j
        else:
            raise ValueError("Invalid Border style")
        
        c = cb1+cb2+cb3+cb4+cc1+cc2
        
        self.vlist.colors = c

class Progressbar(Widget):
    """
    Progressbar displaying a progress of any action to the user.
    
    By default, this Widget uses :py:class:`ProgressbarBackground` as its Background class.
    
    The border and borderstyle options are the same as for the :py:class:`peng3d.gui.button.Button` Widget.
    
    The two colors given are for left and right, respectively. This may be used to create gradients.
    
    ``nmin``\ , ``nmax`` and ``n`` represent the minimal value, maximal value and current value, respectively.
    Unexpected behaviour may occur if the minimal value is bigger then the maximum value.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None,
                 nmin=0,nmax=100,n=0,
                 border=[4,4],
                 borderstyle="flat",
                 colors=[[240,119,70],[240,119,70]]
                 ):
        self._nmin = nmin
        self._nmax = nmax
        self._n = n
        if bg is None:
            bg = ProgressbarBackground(self,border,borderstyle,colors)
        super(Progressbar,self).__init__(name,submenu,window,peng,pos,size,bg)
        self.redraw()
    
    @property
    def nmin(self):
        """
        Property representing the minimal value of the progressbar. Typically ``0``\ .
        """
        return self._nmin
    @nmin.setter
    def nmin(self,value):
        self._nmin = value
        self.redraw()
    
    @property
    def nmax(self):
        """
        Property representing the maximum value of the progressbar. Typically ``100`` to represent percentages easily.
        """
        return self._nmax
    @nmax.setter
    def nmax(self,value):
        self._nmax = value
        self.redraw()
    
    @property
    def n(self):
        """
        Property representing the current value of the progressbar.
        
        Changing this property will activate the ``progresschange`` action.
        """
        return self._n
    @n.setter
    def n(self,value):
        value = min(max(value,self.nmin),self.nmax)
        if self._n != value:
            self.doAction("progresschange")
        self._n = value
        self.redraw()
    
    @property
    def value(self):
        """
        Alias to the :py:attr:`n` property.
        """
        return self._n
    @value.setter
    def value(self,value):
        value = min(max(value,self.nmin),self.nmax)
        if self._n != value:
            self.doAction("progresschange")
        self._n = value
        self.redraw()


class SliderBackground(ButtonBackground):
    """
    Background for the :py:class:`Slider` Widget.
    
    This background displays a button-like handle on top of a bar representing the selectable range.
    
    All given parameters will affect the handle.
    """
    def init_bg(self):
        self.vlist_bg = self.submenu.batch2d.add(4,GL_QUADS,None,
            "v2f",
            "c3B",
            )
        super(SliderBackground,self).init_bg()
    def redraw_bg(self):
        # Convenience variables
        #sx,sy = self.widget.size
        #x,y = self.widget.pos
        sx,sy = self.widget.handlesize
        bx,by = self.border
        x,y = self.widget.pos[0]+(self.widget.size[0]-bx*2)*self.widget.p,self.widget.pos[1]
        
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
        
        if self.borderstyle == "flat":
            # Flat style makes no difference between normal,hover and pressed
            cb1 = i+i+i+i
            cb2 = i+i+i+i
            cb3 = i+i+i+i
            cb4 = i+i+i+i
            cc  = i+i+i+i
        elif self.borderstyle == "gradient":
            if self.widget.pressed:
                i = s
            elif self.widget.is_hovering:
                i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            cb1 = i+i+o+o
            cb2 = i+o+o+i
            cb3 = o+o+i+i
            cb4 = o+i+i+o
            cc  = i+i+i+i
        elif self.borderstyle == "oldshadow":
            if self.widget.pressed:
                i = s
                s,h = h,s
            elif self.widget.is_hovering:
                i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
                s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
            cb1 = h+h+h+h
            cb2 = s+s+s+s
            cb3 = s+s+s+s
            cb4 = h+h+h+h
            cc  = i+i+i+i
        elif self.borderstyle == "material":
            if self.widget.pressed:
                i = [max(bg[0]-20,0),max(bg[1]-20,0),max(bg[2]-20,0)]
            elif self.widget.is_hovering:
                i = [max(bg[0]-10,0),max(bg[1]-10,0),max(bg[2]-10,0)]
            cb1 = s+s+o+o
            cb2 = s+o+o+s
            cb3 = o+o+s+s
            cb4 = o+s+s+o
            cc  = i+i+i+i
        else:
            raise ValueError("Invalid Border style")
        
        c = cb1+cb2+cb3+cb4+cc
        
        self.vlist.colors = c
        
        sx,sy = self.widget.size
        x,y = self.widget.pos
        bx,by = self.border
        
        #    x          y
        v5 = x+bx,      y+sy-by
        v6 = x+sx-bx,   y+sy-by
        v7 = x+bx,      y+by
        v8 = x+sx-bx,   y+by
        
        qbg = v7+v8+v6+v5
        
        cbg = [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]*4
        
        self.vlist_bg.vertices = qbg
        self.vlist_bg.colors=cbg

class Slider(Progressbar):
    """
    Slider that can be used to get a number from the user.
    
    By default, this Widget uses :py:class:`SliderBackground` as its Background class.
    
    Most options are the same as for :py:class:`Progressbar`\ .
    
    ``handlesize`` simply determines the size of the handle.
    
    Note that scaling this widget on the y-axis will not do much, scale the handlesize instead.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],bg=None,
                 border=[4,4], borderstyle="flat",
                 nmin=0,nmax=100,n=0,
                 handlesize=[16,24],
                 ):
        self.handlesize = handlesize
        if bg is None:
            bg = SliderBackground(self,border,borderstyle)
        super(Slider,self).__init__(name,submenu,window,peng,pos,size,bg,nmin,nmax,n)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        if not self.pressed:
            return
        totx = self.size[0]-self.bg.border[0]*2
        x = x-self.pos[0]-self.bg.border[0]
        x = min(max(x,0),totx)
        n = int(((x/totx)*(self.nmax-self.nmin))+.5)+self.nmin
        n = min(max(n,self.nmin),self.nmax)
        self.n = n
    
    @property
    def p(self):
        """
        Helper property containing the percentage this slider is "filled".
        
        This property is read-only.
        """
        return (self.n-self.nmin)/(self.nmax-self.nmin)

