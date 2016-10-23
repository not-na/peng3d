#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  button.py
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
    "Button","ButtonBackground",
    "ImageButton","ImageBackground",
    "FramedImageButton","FramedImageBackground",
    "ToggleButton",
    "Checkbox","CheckboxBackground"
]

import pyglet
from pyglet.gl import *

from .widgets import Background,Widget

LABEL_FONT_SIZE = 16


class ButtonBackground(Background):
    """
    Background for the :py:class:`Button` Widget.
    
    This background renders the button and its border, but not the label.
    """
    def __init__(self,widget,border,borderstyle="flat"):
        self.border = border
        self.borderstyle = borderstyle
        super(ButtonBackground,self).__init__(widget)
    def init_bg(self):
        self.vlist = self.submenu.batch2d.add(20,GL_QUADS,None,
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

class Button(Widget):
    """
    Button Widget allowing the user to trigger specific actions.
    
    By default, this Widget uses :py:class:`ButtonBackground` as its Background class.
    
    The border given is in pixels from the left/right and top/bottom, respectively.
    
    The borderstyle may be either ``flat``\ , which has no border at all, 
    ``gradient``\ , which fades from the inner color to the background color, 
    ``oldshadow``\ , which uses a simple fake shadow with the light from the top-left corner and
    ``material``\ , which imitates Google Material Design shadows.
    
    Also, the label of the button may only be a single line of text, anything else may produce undocumented behaviour.
    
    If neccessary, the font size of the Label may be changed via the global Constant :py:data:`LABEL_FONT_SIZE`\ , changes will only apply to Buttons created after change.
    The text color used is ``[62,67,73,255]`` in RGBA and the font used is Arial, which should be available on most systems.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],bg=None,
                 border=[4,4], borderstyle="flat",
                 label="Button"):
        if bg is None:
            bg = ButtonBackground(self,border,borderstyle)
        super(Button,self).__init__(name,submenu,window,peng,pos,size,bg)
        self._label = pyglet.text.Label(label,
                font_name="Arial",
                font_size=LABEL_FONT_SIZE,
                color=[62,67,73,255],
                x=0,y=0,
                batch=self.submenu.batch2d,
                anchor_x="center", anchor_y="center"
                )
        self.redraw()
        
        # Redraws the button every 2 seconds to prevent glitched graphics
        pyglet.clock.schedule_interval(self.redraw,2)
    
    def draw(self):
        """
        Draws the button and its Label.
        """
        super(Button,self).draw()
        self._label.draw()
    
    def redraw(self,dt=None):
        super(Button,self).redraw()
        self.redraw_label()
    redraw.__noautodoc__ = True
    def redraw_label(self):
        """
        Re-draws the label by calculating its position.
        
        Currently, the label will always be centered on the Button.
        """
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        
        # Label position
        self._label.x = x+sx/2.
        self._label.y = y+sy/2.
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
    
    @property
    def label(self):
        """
        Property for accessing the label of this Button.
        """
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

class ImageBackground(Background):
    """
    Background for the :py:class:`ImageButton` Widget.
    
    This background renders a image given based on whether the widget is pressed, hovered over or disabled.
    
    It should also be possible to use this class as a background for most other Widgets.
    """
    def __init__(self,widget,bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None):
        bg = bg_idle
        self.bg_texinfo = bg
        if bg_hover is None:
            assert bg_hover[1]==self.bg_texinfo[1] # see init_bg()
            self.bg_hover=bg
        else:
            self.bg_hover=bg_hover
        if bg_disabled is None:
            assert bg_disabled[1]==self.bg_texinfo[1] # see init_bg()
            self.bg_disabled=bg
        else:
            self.bg_disabled=bg_disabled
        if bg_pressed is None:
            assert bg_pressed[1]==self.bg_texinfo[1] # see init_bg()
            self.bg_pressed=bg
        else:
            self.bg_pressed=bg_pressed
        super(ImageBackground,self).__init__(widget)
    def init_bg(self):
        # TODO: add seperate groups per active texture, in case the different images are on different textures
        self.bg_group = pyglet.graphics.TextureGroup(_FakeTexture(*self.bg_texinfo))
        self.vlist_bg = self.submenu.batch2d.add(4,GL_QUADS,self.bg_group,
            "v2f",
            ("t3f",self.bg_texinfo[2]),
            )
    def redraw_bg(self):
        # Convenience variables
        sx,sy = self.widget.size
        x,y = self.widget.pos
        
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
        
        if not self.widget.enabled:
            self.vlist_bg.tex_coords = self.bg_disabled[2]
        elif self.widget.pressed:
            self.vlist_bg.tex_coords = self.bg_pressed[2]
        elif self.widget.is_hovering:
            self.vlist_bg.tex_coords = self.bg_hover[2]
        else:
            self.vlist_bg.tex_coords = self.bg_texinfo[2]

class ImageButton(Button):
    """
    Subclass of :py:class:`Button` using an image as a background instead.
    
    By default, this Widget uses :py:class:`ImageBackground` as its Background class.
    
    There are no changes to any other mechanics of the Button, only visually.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],bg=None,
                 label="Button",
                 bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],
                 bg_hover=None,
                 bg_disabled=None,
                 bg_pressed=None,
                 ):
        if bg is None:
            bg = ImageBackground(self,bg_idle,bg_hover,bg_disabled,bg_pressed)
        super(ImageButton,self).__init__(name,submenu,window,peng,pos,size,bg,label=label)


class FramedImageBackground(ImageBackground):
    """
    Background for the :py:class:`FramedImageButton` Widget.
    
    This background is similiar to :py:class:`ImageBackground`\ , but it attempts to scale smarter with less artifacts.
    
    Note that this feature is currently not working properly, and will thus output a warning on the console if tried to use.
    """
    def __init__(self,widget,bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None,frame_size=[[2,10,2],[2,10,2]]):
        print("Use FramedImageBackground with care, may produce graphical glitches and crashes")
        # TODO: fix this
        self.frame_size = frame_size
        self.repeat_edge=True
        self.repeat_center=True
        super(FramedImageBackground,self).__init__(widget,bg_idle,bg_hover,bg_disabled,bg_pressed)
    def init_bg(self):
        self.bg_group = pyglet.graphics.TextureGroup(_FakeTexture(*self.bg_texinfo))
        self.vlist_bg = self.submenu.batch2d.add(36,GL_QUADS,self.bg_group,
            "v2f",
            "t3f",
            )
    def redraw_bg(self):
        # Convenience variables
        sx,sy = self.widget.size
        x,y = self.widget.pos
        fx,fy = self.frame_size
        osx,osy = sum(fx),sum(fy)
        bsx = (osx/osy)*sy
        bsy = (osx/osy)*sy
        # frame-axis-left/right/center/up/down
        fxl,fxc,fxr = fx
        fyu,fyc,fyd = fy
        
        fxl,fxc,fxr = (fxl/sum(fx))*bsx, (fxc/sum(fx))*bsx, (fxr/sum(fx))*bsx
        fyu,fyc,fyd = (fyu/sum(fy))*bsy, (fyc/sum(fy))*bsy, (fyd/sum(fy))*bsy
        
        #assert fxl+fxc+fxr==sx
        #assert fyu+fyc+fyd==sy
        # To avoid confusion when supplied invalid numbers
        
        # 16 Vertices according to button_scheme.xcf
        
        v1  = x,         y+sy
        v2  = x+fxl,     y+sy
        v3  = x+sx-fxr,  y+sy
        v4  = x+sx,      y+sy
        v5  = x+sx,      y+sy-fyu
        v6  = x+sx,      y+fyd
        v7  = x+sx,      y
        v8  = x+sx-fxr,  y
        v9  = x+fxl,     y
        v10 = x,         y
        v11 = x,         y+fyd
        v12 = x,         y+sy-fyu
        v13 = x+fxl,     y+sy-fyu
        v14 = x+sx-fxr,  y+sy-fyu
        v15 = x+sx-fxr,  y+fyd
        v16 = x+fxl,     y+fyd
        
        bv1  = x,         y+bsy
        bv2  = x+fxl,     y+bsy
        bv3  = x+bsx-fxr,  y+bsy
        bv4  = x+bsx,      y+bsy
        bv5  = x+bsx,      y+bsy-fyu
        bv6  = x+bsx,      y+fyd
        bv7  = x+bsx,      y
        bv8  = x+bsx-fxr,  y
        bv9  = x+fxl,     y
        bv10 = x,         y
        bv11 = x,         y+fyd
        bv12 = x,         y+bsy-fyu
        bv13 = x+fxl,     y+bsy-fyu
        bv14 = x+bsx-fxr,  y+bsy-fyu
        bv15 = x+bsx-fxr,  y+fyd
        bv16 = x+fxl,     y+fyd
        
        qc1 = v10+v9 +v16+v11
        qc2 = v12+v13+v2 +v1 
        qc3 = v14+v5 +v4 +v3 
        qc4 = v8 +v7 +v6 +v15
        
        #qe1 = bv9 +bv8 +bv15+bv16
        #qe2 = bv11+bv16+bv13+bv12
        #qe3 = bv13+bv14+bv3 +bv2 
        #qe4 = bv15+bv6 +bv5 +bv14
        qe1 = v9 +v8 +v15+v16
        qe2 = v11+v16+v13+v12
        qe3 = v13+v14+v3 +v2 
        qe4 = v15+v6 +v5 +v14
        
        qc = v16+v15+v14+v13
        
        v = qc1+qc2+qc3+qc4+qe1+qe2+qe3+qe4+qc
        
        # Texture Coords
        if not self.widget.enabled:
            texcoords = self.bg_disabled[2]
        elif self.widget.pressed:
            texcoords = self.bg_pressed[2]
        elif self.widget.is_hovering:
            texcoords = self.bg_hover[2]
        else:
            texcoords = self.bg_texinfo[2]
        print("###")
        print(self.widget.enabled,self.widget.pressed,self.widget.is_hovering)
        print(texcoords)
        x,y,_,sx,_,_,_,sy,_,_,_,_ = texcoords
        sx,sy=sx-x,sy-y
        asx,asy = min(sx,(osx/osy)*sx),min(sy,(osx/osy)*sx)
        fxl,fxc,fxr=(fx[0]/sum(fx))*sx, (fx[1]/sum(fx))*sx, (fx[2]/sum(fx))*sx
        fyu,fyc,fyd=(fy[0]/sum(fy))*sy, (fy[1]/sum(fy))*sy, (fy[2]/sum(fy))*sy
        
        print(x,y,sx,sy)
        print(fxl,fxc,fxr)
        print(fyu,fyc,fyd)
        print("###")
        
        assert fxl+fxc+fxr==sx
        assert fyu+fyc+fyd==sy
        
        t1  = x,         y+sy,      0
        t2  = x+fxl,     y+sy,      0
        t3  = x+sx-fxr,  y+sy,      0
        t4  = x+sx,      y+sy,      0
        t5  = x+sx,      y+sy-fyu,  0
        t6  = x+sx,      y+fyd,     0
        t7  = x+sx,      y,         0
        t8  = x+sx-fxr,  y,         0
        t9  = x+fxl,     y,         0
        t10 = x,         y,         0
        t11 = x,         y+fyd,     0
        t12 = x,         y+sy-fyu,  0
        t13 = x+fxl,     y+sy-fyu,  0
        t14 = x+sx-fxr,  y+sy-fyu,  0
        t15 = x+sx-fxr,  y+fyd,     0
        t16 = x+fxl,     y+fyd,     0
        
        at1  = x,         y+asy,      0
        at2  = x+fxl,     y+asy,      0
        at3  = x+asx-fxr,  y+asy,      0
        at4  = x+asx,      y+asy,      0
        at5  = x+asx,      y+asy-fyu,  0
        at6  = x+asx,      y+fyd,     0
        at7  = x+asx,      y,         0
        at8  = x+asx-fxr,  y,         0
        at9  = x+fxl,     y,         0
        at10 = x,         y,         0
        at11 = x,         y+fyd,     0
        at12 = x,         y+asy-fyu,  0
        at13 = x+fxl,     y+asy-fyu,  0
        at14 = x+asx-fxr,  y+asy-fyu,  0
        at15 = x+asx-fxr,  y+fyd,     0
        at16 = x+fxl,     y+fyd,     0
        
        
        
        tqc1 = t10+t9 +t16+t11
        tqc2 = t12+t13+t2 +t1 
        tqc3 = t14+t5 +t4 +t3 
        tqc4 = t8 +t7 +t6 +t15
        
        # size of center x size adjusted
        #fxcr = (fx[1]/sum(fx))*bsx
        # rel x pos of v3 in P
        #xv3 = self.widget.size[0]-(self.widget.size[0]*((fx[2]/sum(fx))))
        xv3 = v3[0]-self.widget.pos[0]
        xv2 = v2[0]-self.widget.pos[0]
        #xv2 = self.widget.size[0]*(fx[0]/sum(fx))
        #txr = (fxcr/self.widget.size[0])*(self.widget.size[0]+((fx[2]/sum(fx))*bsx))
        #  P   Ratio of (center-x-size adjusted) to x-size applied to (x-size plus (right-x-size adjusted))
        #txr = fxl+(self.widget.size[0]*((fx[2]/sum(fx))))
        #  T   Left-x-size not adjusted plus x-size times (ratio of right-x-size to total)
        #txr = sx-fxr # Default
        #  T   x-size minus right-x-size not adjusted
        #txr = (max((xv3-xv2),fx[1])/self.widget.size[0])*sx
        print(fx[1]/sum(fx))
        txr = (fx[1]/sum(fx))*asx
        #  P  ratio of (xv3 rel to xv2) to x-size
        
        
        txr = x+txr
        
        xt2  = x+fxl,     y+asy,      0
        xt13 = x+fxl,     y+asy-fyu,  0
        xt16 = x+fxl,     y+fyd,     0
        xt9  = x+fxl,     y,         0
        
        xt8  = txr,  y,         0
        xt15 = txr,  y+fyd,     0
        xt14 = txr,  y+asy-fyu,  0
        xt3  = txr,  y+asy,      0
        
        
        yt6  = x+asx,      y+fyd,     0
        yt15 = x+asx-fxr,  y+fyd,     0
        yt11 = x,         y+fyd,     0
        yt16 = x+fxl,     y+fyd,     0
        
        yt12 = x,         y+asy-fyu,  0
        yt13 = x+fxl,     y+asy-fyu,  0
        yt5  = x+asx,      y+asy-fyu,  0
        yt14 = x+asx-fxr,  y+asy-fyu,  0
        
        tqe1 = xt9 +xt8 +xt15+xt16
        tqe2 = yt11+yt16+yt13+yt12
        tqe3 = xt13+xt14+xt3 +xt2 
        tqe4 = yt15+yt6 +yt5 +yt14
        
        #tqe1 = at9 +at8 +at15+at16
        #tqe2 = at11+at16+at13+at12
        #tqe3 = at13+at14+at3 +at2 
        #tqe4 = at15+at6 +at5 +at14
        
        #tqe1 = t9 +t8 +t15+t16
        #tqe2 = t11+t16+t13+t12
        #tqe3 = t13+t14+t3 +t2 
        #tqe4 = t15+t6 +t5 +t14
        
        tqc = t16+t15+t14+t13
        
        t = tqc1+tqc2+tqc3+tqc4+tqe1+tqe2+tqe3+tqe4+tqc
        #print(t)
        #print(v)
        self.vlist_bg.vertices=v
        self.vlist_bg.tex_coords=t

class FramedImageButton(ImageButton):
    """
    Subclass of :py:class:`ImageButton` adding smart scaling to the background.
    
    By default, this Widget uses :py:class:`FramedImageBackground` as its Background class.
    
    Note that this feature is currently not working properly, and will thus output a warning on the console if tried to use.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],bg=None,
                 label="Button",
                 bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],
                 bg_hover=None,
                 bg_disabled=None,
                 bg_pressed=None,
                 frame_size=[[2,10,2],[2,10,2]],
                 ):
        if bg is None:
            bg = FramedImageBackground(self,bg_idle,bg_hover,bg_disabled,bg_pressed,frame_size)
        super(FramedImageButton,self).__init__(name,submenu,window,peng,pos,size,bg,label=label)


class ToggleButton(Button):
    """
    Variant of :py:class:`Button` that stays pressed until clicked again.
    
    This widgets adds the following actions:
    
    - ``press_down`` is called upon depressing the button
    - ``press_up`` is called upon releasing the button
    - ``click`` is changed to be called on every click on the button, e.g. like ``press_down`` and ``press_up`` combined
    """
    def on_mouse_press(self,x,y,button,modifiers):
        if not self.clickable:
            return
        elif mouse_aabb([x,y],self.size,self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("click")
                self.pressed = not self.pressed
                if self.pressed:
                    self.doAction("press_down")
                else:
                    self.doAction("press_up")
            elif button == pyglet.window.mouse.RIGHT:
                self.doAction("context")
            self.redraw()
    def on_mouse_release(self,x,y,button,modifiers):
        pass


class CheckboxBackground(ButtonBackground):
    """
    Background for the :py:class:`Checkbox` Widget.
    
    This background looks like a button, but adds a square in the middle if it is pressed.
    
    The color of the square defaults to a tone of orange commonly found in GTK GUIs on Ubuntu.
    """
    def __init__(self,widget,borderstyle,checkcolor=[240,119,70]):
        self.checkcolor = checkcolor
        super(CheckboxBackground,self).__init__(widget,[3,3],borderstyle)
    def init_bg(self):
        self.vlist = self.submenu.batch2d.add(20,GL_QUADS,None,
            "v2f",
            "c3B",
            )
        self.vlist_check = self.submenu.batch2d.add(4,GL_QUADS,None,
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
        
        if self.borderstyle == "flat":
            if self.widget.pressed:
                i = s
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
        
        # Cross
        
        # Old method that displayed a tick
        """if not self.widget.pressed:
            self.vlist_cross.colors = 6*bg
        else:
            if self.borderstyle=="flat":
                c = [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]
            elif self.borderstyle=="gradient":
                c = h
            elif self.borderstyle=="oldshadow":
                c = h
            elif self.borderstyle=="material":
                c = s
            self.vlist_cross.colors = 6*c
        
        # Convenience variables
        sx,sy = self.widget.size
        x,y = self.widget.pos
        bx,by = self.border
        
        v1 = x+bx,      y+(sy-by*2)/2+by
        v2 = x+sx/2,    y+(sy-by*2)/4+by
        v3 = v6
        v4 = x+sx,      y+sy
        v5 = x+sx/2,    y+by
        v6 = x+bx,      y+(sy-by*2)/4+by
        
        self.vlist_cross.vertices = v2+v1+v6+v5+v4+v3"""
        
        # TODO: add better visual indicator
        
        v1 = x+bx*1.5,    y+sy-by*1.5
        v2 = x+sx-bx*1.5, y+sy-by*1.5
        v3 = x+bx*1.5,    y+by*1.5
        v4 = x+sx-bx*1.5, y+by*1.5
        
        self.vlist_check.colors = self.checkcolor*4 if self.widget.pressed else i*4
        self.vlist_check.vertices = v3+v4+v2+v1

class Checkbox(ToggleButton):
    """
    Variant of :py:class:`ToggleButton` using a different visual indicator.
    
    By default, this Widget uses :py:class:`CheckboxBackground` as its Background class.
    
    Note that the position and size given are for the indicator, the label will be bigger than the given size.
    
    The label given will be displayed to the right of the Checkbox.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=[100,24],bg=None,
                 borderstyle="flat",
                 label="Checkbox",
                 checkcolor=[240,119,70]):
        if bg is None:
            bg = CheckboxBackground(self,borderstyle,checkcolor)
        super(Checkbox,self).__init__(name,submenu,window,peng,pos,size,bg,borderstyle=borderstyle,label=label)
    def redraw_label(self):
        """
        Re-calculates the position of the Label.
        """
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        
        # Label position
        self._label.anchor_x = "left"
        self._label.x = x+sx/2.+sx
        self._label.y = y+sy/2.+sy*.15
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
