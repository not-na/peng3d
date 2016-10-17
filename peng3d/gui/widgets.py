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

__all__ = ["Widget","Button","ImageButton"]

import time

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode

def mouse_aabb(mpos,size,pos):
    return pos[0]<=mpos[0]<=pos[0]+size[0] and pos[1]<=mpos[1]<=pos[1]+size[1]

LABEL_FONT_SIZE = 16

class Widget(object):
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
            return self._size(self.window.width,self.window.height,*self.pos)
        else:
            raise TypeError("Invalid size type")
    
    @property
    def clickable(self):
        return self.submenu.name == self.submenu.menu.activeSubMenu and self.submenu.menu.name == self.window.activeMenu
    
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

class Button(Widget):
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],
                 border=[4,4], borderstyle="flat",
                 label="Button"):
        super(Button,self).__init__(name,submenu,window,peng,pos,size)
        self._label = pyglet.text.Label(label,
                font_name="Arial",
                font_size=LABEL_FONT_SIZE,
                color=[62,67,73,255],
                x=0,y=0,
                batch=self.submenu.batch2d,
                anchor_x="center", anchor_y="center"
                )
        self.border = border
        self.borderstyle = borderstyle
        self.init_bg()
        self.redraw()
        
        # Redraws the button every 2 seconds to prevent glitched graphics
        pyglet.clock.schedule_interval(self.redraw,2)
    
    def init_bg(self):
        self.vlist = self.submenu.batch2d.add(20,GL_QUADS,None,
            "v2f",
            "c3B",
            )
        self.vlists.append([self.vlist,GL_QUADS])
    
    def draw(self):
        super(Button,self).draw()
        self._label.draw()
    
    def redraw(self,dt=None):
        self.redraw_bg()
        self.redraw_label()
    def redraw_label(self):
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        bx,by = self.border
        
        # Label position
        self._label.x = x+sx/2.
        self._label.y = y+sy/2.
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
    def redraw_bg(self):
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
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
        
        if self.borderstyle == "flat":
            # Flat style makes no difference between normal,hover and pressed
            cb1 = i+i+i+i
            cb2 = i+i+i+i
            cb3 = i+i+i+i
            cb4 = i+i+i+i
            cc  = i+i+i+i
        elif self.borderstyle == "gradient":
            if self.pressed:
                i = s
            elif self.is_hovering:
                i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            cb1 = i+i+o+o
            cb2 = i+o+o+i
            cb3 = o+o+i+i
            cb4 = o+i+i+o
            cc  = i+i+i+i
        elif self.borderstyle == "oldshadow":
            if self.pressed:
                i = s
                s,h = h,s
            elif self.is_hovering:
                i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
                s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
            cb1 = h+h+h+h
            cb2 = s+s+s+s
            cb3 = s+s+s+s
            cb4 = h+h+h+h
            cc  = i+i+i+i
        elif self.borderstyle == "material":
            if self.pressed:
                i = [max(bg[0]-20,0),max(bg[1]-20,0),max(bg[2]-20,0)]
            elif self.is_hovering:
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
    
    @property
    def label(self):
        return self._label.text
    @label.setter
    def label(self,label):
        self._label.text = label

class _FakeTexture(object):
    def __init__(self,target,texid,texcoords):
        self.target = target
        self.id = texid
        self.tex_coords = texcoords
        self.anchor_x = 0
        self.anchor_y = 0

#class TextureGroup(pyglet.graphics.TextureGroup):
#    def unset_state(self):
#        super(TextureGroup,self).unset_state()
#        print("unset State %.4f"%time.time())
#        pass

class ImageButton(Button):
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],
                 label="Button",
                 bg=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12]
                 ):
        self.bg_texinfo = bg
        #if len(self.bg_texinfo[2])==12:
        #    self.bg_texinfo[2]=list(self.bg_texinfo[2])
        #    del self.bg_texinfo[2][2]
        #    del self.bg_texinfo[2][4]
        #    del self.bg_texinfo[2][6]
        #    del self.bg_texinfo[2][8]
        #print(self.bg_texinfo)
        super(ImageButton,self).__init__(name,submenu,window,peng,pos,size,label=label)
    def init_bg(self):
        # Currently disabled due to extremely buggy behaviour
        return
        self.bg_group = pyglet.graphics.TextureGroup(_FakeTexture(*self.bg_texinfo))
        self.vlist_bg = self.submenu.batch2d.add(4,GL_QUADS,self.bg_group,
            "v2f",
            ("t3f",self.bg_texinfo[2]),
            )
        self.vlists.append([self.vlist_bg,GL_QUADS])
    def redraw_bg(self):
        # Currently disabled due to extremely buggy behaviour
        return
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        bx,by = self.border
        
        # Button background
        
        # Outer vertices
        #    x          y
        v1 = x,         y+sy
        v2 = x+sx,      y+sy
        v3 = x,         y
        v4 = x+sx,      y
        
        q = v3+v4+v2+v1
        
        self.vlist_bg.vertices = q
        
        # Textures
        
        #self.vlist_bg.tex_coords = self.bg_texinfo[2]
        #self.vlist_bg.tex_coords = [0,0,1,0,1,1,0,1]
        #self.vlist_bg.tex_coords = [0,0,0,1,0,0,1,1,0,0,1,0]
        #print(list(self.vlist_bg.tex_coords))
        #print(list(self.vlist_bg.vertices))
    def draw(self):
        # Very hacky code because my own code doesn't seem to work at all
        pyglet.image.Texture.blit(_FakeTexture(*self.bg_texinfo),x=self.pos[0],y=self.pos[1],width=self.size[0],height=self.size[1])
        super(ImageButton,self).draw()
