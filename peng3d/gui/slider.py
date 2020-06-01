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
    "AdvancedProgressbar",
    "Slider","SliderBackground",
    "VerticalSlider","VerticalSliderBackground",
]

import pyglet
from pyglet.gl import *

from .widgets import Background,Widget
from .button import ButtonBackground

basestring = str # for py2 compat, may get dropped at a later release

class ProgressbarBackground(Background):
    """
    Background for the :py:class:`Progressbar` Widget.
    
    This background displays a bar with a border similar to :py:class:`ButtonBackground`\ .
    Note that two colors may be given, one for the left and one for the right.
    """
    def __init__(self,widget,border,borderstyle,colors):
        super(ProgressbarBackground,self).__init__(widget)
        self.border = border
        self.borderstyle = borderstyle
        self.colors = colors
    def init_bg(self):
        self.vlist = self.submenu.batch2d.add(24,GL_QUADS,pyglet.graphics.OrderedGroup(1),
            "v2f",
            "c3B",
            )
        self.reg_vlist(self.vlist)
    def redraw_bg(self):
        x,y = self.widget.pos
        sx,sy = self.widget.size
        bx,by = self.border
        
        nmin,nmax,n = self.widget.nmin,self.widget.nmax,float(self.widget.n)
        if (nmax-nmin)==0:
            p = 0 # prevents ZeroDivisionError
        else:
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
    Unexpected behavior may occur if the minimal value is bigger then the maximum value.
    """

    IS_CLICKABLE = True
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None,
                 nmin=0,nmax=100,n=0,
                 border=[4,4],
                 borderstyle=None,
                 colors=[[240,119,70],[240,119,70]],
                 ):
        borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle
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
        return self.n
    @value.setter
    def value(self,value):
        # May be a tiny bit slower, but safer if n is changed
        self.n = value

class AdvancedProgressbar(Progressbar):
    """
    Advanced Progressbar displaying the combined progress through multiple actions.
    
    Visually, this widget is identical to :py:class:`Progressbar` with the only difference
    being the way the progress percentage is calculated.
    
    The ``offset_nmin``\ , ``offset_n`` and ``offset_nmax`` parameters are equivalent
    to the parameters of the same name minus the ``offset_`` prefix.
    
    ``categories`` may be any dictionary mapping category names to 3-tuples of
    format ``(nmin,n,nmax)``\ .
    
    It is possible to read, write and delete categories through the ``widget[cat]`` syntax.
    Note however, that modifying categories in-place, e.g. like ``widget[cat][1]=100``\ , 
    requires a manual call to :py:meth:`redraw()`\ .
    
    When setting the :py:attr:`nmin`\ , :py:attr:`n` or :py:attr:`nmax` properties, only
    an internal offset value will be modified. This may result in otherwise unexpected behavior
    if setting e.g. ``n`` to ``nmax`` because the categories may influence the total percentage calculation.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None,
                 categories={},
                 offset_nmin=0,offset_nmax=0,offset_n=0,
                 border=[4,4],
                 borderstyle=None,
                 colors=[[240,119,70],[240,119,70]],
                 ):
        super(AdvancedProgressbar,self).__init__(name,submenu,window,peng,pos,size,bg,offset_nmin,offset_nmax,offset_n,border,borderstyle,colors)
        
        self.categories = categories
        for cname,cdat in self.categories.items():
            assert len(cdat)==3 # nmin,n,nmax
    
    @property
    def nmin(self):
        return self._nmin+sum(map(lambda cdat:cdat[0],self.categories.values()))
    @nmin.setter
    def nmin(self,value):
        # may confuse users if base_nmax is very low but the categories nmax is high
        # may also prevent the expected behavior that if n is set to nmin, p is equal to 0%
        self._nmin = value
        self.redraw()
    
    @property
    def n(self):
        return self._n+sum(map(lambda cdat:cdat[1],self.categories.values()))
    @n.setter
    def n(self,value):
        # see nmin for information about some of the implications of this behavior
        self._n = value
        self.redraw()
    
    @property
    def nmax(self):
        return self._nmax+sum(map(lambda cdat:cdat[2],self.categories.values()))
    @nmax.setter
    def nmax(self,value):
        # see nmin for information about some of the implications of this behavior
        self._nmax = value
        self.redraw()
    
    def __getitem__(self,key):
        # returns the 3-tuple associated with the category
        if key not in self.categories:
            raise KeyError("No Category with name '%s'"%key)
        return self.categories[key]
        # TODO: automatically redraw if list returned here is modified
    def __setitem__(self,key,value):
        # sets the 3-tuple associated with the category
        # mostly used for category creation, since expressions of the form
        # widget[category][0]=1 will only use __getitem__ and modify data in-place
        assert isinstance(key,basestring) # py2 compat is done at the top
        assert len(value)==3 # nmin,n,nmax
        self.categories[key]=list(value) # conversion to list allows in-place modification if a tuple was passed
        self.redraw()
    def __delitem__(self,key):
        if key not in self.categories:
            raise KeyError("No Category with name '%s'"%name)
        del self.categories[key]
        self.redraw()
    
    def addCategory(self,name,nmin=0,n=0,nmax=100):
        """
        Adds a category with the given name.
        
        If the category already exists, a :py:exc:`KeyError` will be thrown. Use
        :py:meth:`updateCategory()` instead if you want to update a category.
        """
        assert isinstance(name,basestring) # py2 compat is done at the top
        if name in self.categories:
            raise KeyError("Category with name '%s' already exists"%name)
        self.categories[name]=[nmin,n,nmax]
        self.redraw()
    def updateCategory(self,name,nmin=None,n=None,nmax=None):
        """
        Smartly updates the given category.
        
        Only values that are given will be updated, others will be left unchanged.
        
        If the category does not exist, a :py:exc:`KeyError` will be thrown. Use
        :py:meth:`addCategory()` instead if you want to add a category.
        """
        # smart update, only stuff that was given
        if name not in self.categories:
            raise KeyError("No Category with name '%s'"%name)
        if nmin is not None:
            self.categories[name][0]=nmin
        if n is not None:
            self.categories[name][1]=n
        if nmax is not None:
            self.categories[name][2]=nmax
        self.redraw()
        self.doAction("progresschange")
    def deleteCategory(self,name):
        """
        Deletes the category with the given name.
        
        If the category does not exist, a :py:exc:`KeyError` will be thrown.
        """
        if name not in self.categories:
            raise KeyError("No Category with name '%s'"%name)
        del self.categories[name]
        self.redraw()

class SliderBackground(ButtonBackground):
    """
    Background for the :py:class:`Slider` Widget.
    
    This background displays a button-like handle on top of a bar representing the selectable range.
    
    All given parameters will affect the handle.
    """
    def init_bg(self):
        self.vlist_bg = self.submenu.batch2d.add(4,GL_QUADS,pyglet.graphics.OrderedGroup(0),
            "v2f",
            "c3B",
            )
        self.reg_vlist(self.vlist_bg)
        super(SliderBackground,self).init_bg()
    def redraw_bg(self):
        super(SliderBackground,self).redraw_bg()
        
        sx,sy,x,y,bx,by = super(SliderBackground,self).getPosSize()
        
        #    x          y
        v5 = x+bx,      y+sy-by
        v6 = x+sx-bx,   y+sy-by
        v7 = x+bx,      y+by
        v8 = x+sx-bx,   y+by
        
        qbg = v7+v8+v6+v5
        
        bg,_,_,_,_ = self.getColors()
        
        cbg = [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]*4
        
        self.vlist_bg.vertices = qbg
        self.vlist_bg.colors=cbg
    
    def getPosSize(self):
        sx,sy = self.widget.handlesize
        bx,by = self.border
        x,y = self.widget.pos[0]+(self.widget.size[0]-bx*2)*self.widget.p,self.widget.pos[1]
        return sx,sy,x,y,bx,by
    getPosSize.__noautodoc__ = True

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
                 border=[4,4], borderstyle=None,
                 nmin=0,nmax=100,n=0,
                 handlesize=[16,24],
                 ):
        borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle
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
        return (self.n-self.nmin)/max((self.nmax-self.nmin),1)


class VerticalSliderBackground(SliderBackground):
    """
    Background for the :py:class:`VerticalSlider` Widget.
    
    This background uses the same technique as :py:class:`SliderBackground`\ , simply turned by 90 Degrees.
    """
    
    def getPosSize(self):
        sx,sy = self.widget.handlesize
        bx,by = self.border
        x,y = self.widget.pos[0],self.widget.pos[1]+(self.widget.size[1]-by*2)*self.widget.p
        return sx,sy,x,y,bx,by
    getPosSize.__noautodoc__ = True

class VerticalSlider(Slider):
    """
    Vertical slider that can be used as a scrollbar or getting other input.
    
    By default, this Widget uses :py:class:`VerticalSliderBackground` as its Background class.
    
    This widget is essentially the same as :py:class:`Slider`\ , only vertical.
    
    Note that you may need to flip the x and y values of ``size``\ , ``handlesize`` and ``border`` compared to :py:class:`Slider`\ .
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[24,100], bg=None,
                 border=[4,4], borderstyle=None,
                 nmin=0,nmax=100,n=0,
                 handlesize=[24,16],
                 ):
        borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle
        if bg is None:
            bg = VerticalSliderBackground(self,border,borderstyle)
        super(VerticalSlider,self).__init__(name,submenu,window,peng,pos,size,bg,border,borderstyle,nmin,nmax,n,handlesize)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        if not self.pressed:
            return
        toty = self.size[1]-self.bg.border[1]*2
        y = y-self.pos[1]-self.bg.border[1]
        y = min(max(y,0),toty)
        n = int(((y/toty)*(self.nmax-self.nmin))+.5)+self.nmin
        n = min(max(n,self.nmin),self.nmax)
        self.n = n
