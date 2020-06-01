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

from .widgets import Background,Widget,mouse_aabb

LABEL_FONT_SIZE = 16


class ButtonBackground(Background):
    """
    Background for the :py:class:`Button` Widget.
    
    This background renders the button and its border, but not the label.
    """
    n_vertices = 20
    change_on_press = True
    vlist_layer = 0 # used as the first argument to OrderedGroup
    
    def __init__(self,widget,border=[4,4],borderstyle="flat",
                 batch=None,change_on_press=None):
        
        super(ButtonBackground,self).__init__(widget)
        
        self.border = border
        self.borderstyle = borderstyle

        self.change_on_press = change_on_press if change_on_press is not None else self.change_on_press
        
        self.borderstyles = {}
        self.addBorderstyle("flat",self.bs_flat)
        self.addBorderstyle("gradient",self.bs_gradient)
        self.addBorderstyle("oldshadow",self.bs_oldshadow)
        self.addBorderstyle("material",self.bs_material)
    def init_bg(self):
        # Can only be initialized here due to order of initialization
        self.vlist = self.submenu.batch2d.add(self.n_vertices,GL_QUADS,pyglet.graphics.OrderedGroup(self.vlist_layer),
            "v2f",
            "c3B",
            )
        self.reg_vlist(self.vlist)
    def redraw_bg(self):
        # Convenience variables
        sx,sy,x,y,bx,by = self.getPosSize()
        
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
        
        if self.borderstyle not in self.borderstyles:
            raise ValueError("Invalid Border style")
        c = self.borderstyles[self.borderstyle](*self.getColors())
        self.vlist.colors = c
    
    def getPosSize(self):
        """
        Helper function converting the actual widget position and size into a usable and offsetted form.
        
        This function should return a 6-tuple of ``(sx,sy,x,y,bx,by)`` where sx and sy are the size, x and y the position and bx and by are the border size.
        
        All values should be in pixels and already include all offsets, as they are used directly for generation of vertex data.
        
        This method can also be overridden to limit the background to a specific part of its widget.
        """
        sx,sy = self.widget.size
        x,y = self.widget.pos
        bx,by = self.border
        return sx,sy,x,y,bx,by
    def getColors(self):
        """
        Overrideable function that generates the colors to be used by various borderstyles.
        
        Should return a 5-tuple of ``(bg,o,i,s,h)``\\ .
        
        ``bg`` is the base color of the background.
        
        ``o`` is the outer color, it is usually the same as the background color.
        
        ``i`` is the inner color, it is usually lighter than the background color.
        
        ``s`` is the shadow color, it is usually quite a bit darker than the background.
        
        ``h`` is the highlight color, it is usually quite a bit lighter than the background.
        """
        bg = self.submenu.bg[:3] if isinstance(self.submenu.bg,list) or isinstance(self.submenu.bg,tuple) else [242,241,240]
        o,i = bg, [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]
        s,h = [max(bg[0]-40,0),max(bg[1]-40,0),max(bg[2]-40,0)], [min(bg[0]+12,255),min(bg[1]+12,255),min(bg[2]+12,255)]
        # Outer,Inner,Shadow,Highlight
        return bg,o,i,s,h
    
    def addBorderstyle(self,name,func):
        """
        Adds a borderstyle to the background object.
        
        Note that borderstyles must be registered seperately for each background object.
        
        ``name`` is the (string) name of the borderstyle.
        
        ``func`` will be called with its arguments as ``(bg,o,i,s,h)``\\ , see :py:meth:`getColors()` for more information.
        """
        self.borderstyles[name]=func
    
    @property
    def pressed(self):
        """
        Read-only helper property to be used by borderstyles for determining if the widget should be rendered as pressed or not.
        
        Note that this property may not represent the actual pressed state, it will always be False if ``change_on_press`` is disabled.
        """
        return self.change_on_press and (self.widget.pressed or getattr(self.widget, "focussed", False))
    @property
    def is_hovering(self):
        """
        Read-only helper property to be used by borderstyles for determining if the widget should be rendered as hovered or not.
        
        Note that this property may not represent the actual hovering state, it will always be False if ``change_on_press`` is disabled.
        """
        return self.change_on_press and self.widget.is_hovering
    
    def bs_flat(self,bg,o,i,s,h):
        # Flat style makes no difference between normal,hover and pressed
        cb1 = i+i+i+i
        cb2 = i+i+i+i
        cb3 = i+i+i+i
        cb4 = i+i+i+i
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    bs_flat.__noautodoc__ = True
    def bs_gradient(self,bg,o,i,s,h):
        if self.pressed:
            i = s
        elif self.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
        cb1 = i+i+o+o
        cb2 = i+o+o+i
        cb3 = o+o+i+i
        cb4 = o+i+i+o
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    bs_gradient.__noautodoc__ = True
    def bs_oldshadow(self,bg,o,i,s,h):
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
        
        return cb1+cb2+cb3+cb4+cc
    bs_oldshadow.__noautodoc__ = True
    def bs_material(self,bg,o,i,s,h):
        if self.pressed:
            i = [max(bg[0]-20,0),max(bg[1]-20,0),max(bg[2]-20,0)]
        elif self.is_hovering:
            i = [max(bg[0]-10,0),max(bg[1]-10,0),max(bg[2]-10,0)]
        cb1 = s+s+o+o
        cb2 = s+o+o+s
        cb3 = o+o+s+s
        cb4 = o+s+s+o
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    bs_material.__noautodoc__ = True

class Button(Widget):
    """
    Button Widget allowing the user to trigger specific actions.
    
    By default, this Widget uses :py:class:`ButtonBackground` as its Background class.
    
    The border given is in pixels from the left/right and top/bottom, respectively.
    
    The borderstyle may be either ``flat``\\ , which has no border at all,
    ``gradient``\\ , which fades from the inner color to the background color,
    ``oldshadow``\\ , which uses a simple fake shadow with the light from the top-left corner and
    ``material``\\ , which imitates Google Material Design shadows.
    
    Also, the label of the button may only be a single line of text, anything else may produce undocumented behavior.
    
    If necessary, the font size of the Label may be changed via the global Constant :py:data:`LABEL_FONT_SIZE`\\ , changes will only apply to Buttons created after change.
    The text color used is ``[62,67,73,255]`` in RGBA and the font used is Arial, which should be available on most systems.
    """

    IS_CLICKABLE = True
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=None,bg=None,
                 border=[4,4], borderstyle=None,
                 label="Button",min_size=None,
                 font_size=None, font=None,
                 font_color=None,
                 label_layer=1,
                 ):
        font = font if font is not None else submenu.font
        font_size = font_size if font_size is not None else submenu.font_size
        font_color = font_color if font_color is not None else submenu.font_color
        borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle
        if bg is None:
            bg = ButtonBackground(self,border,borderstyle)
        super(Button,self).__init__(name,submenu,window,peng,pos,size,bg,min_size)
        self._label = pyglet.text.Label(str(label),
                font_name=font,
                font_size=font_size,
                color=font_color,
                x=0,y=0,
                batch=self.submenu.batch2d,
                group=pyglet.graphics.OrderedGroup(label_layer),
                anchor_x="center", anchor_y="center"
                )
        if getattr(label,"_dynamic",False):
            def f():
                self.label = str(label)
            self.peng.i18n.addAction("setlang",f)
        self.peng.i18n.addAction("setlang",self.redraw) # for dynamic size
        self.redraw()
        
        # Redraws the button every 2 seconds to prevent glitched graphics
        pyglet.clock.schedule_interval(lambda dt:self.redraw(),2)
    
    def on_redraw(self):
        super(Button,self).on_redraw()
        self.redraw_label()
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
        # TODO: make this work with changing languages if previous label was not dynamic
        self._label.text = str(label)
        self.redraw() # necessary for size/pos that depends on label size
    
    def getContentSize(self):
        l = [self._label.content_width,self._label.content_height]
        b = self.bg.border # TODO: make this work with borderless backgrounds
        return [l[0]+b[0]*2,l[1]+b[1]*2]
    
    def delete(self):
        self._label.delete()
        del self._label
        super(Button,self).delete()
    delete.__noautodoc__ = True


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

    vlist_layer = 0
    change_on_press = True

    def __init__(self,widget,bg_idle=None,bg_hover=None,bg_disabled=None,bg_pressed=None):
        self.widget = widget
        bg = self.widget.peng.resourceMgr.normTex(bg_idle, "gui")
        self.bg_texinfo = bg
        if bg_hover is None:
            self.bg_hover=bg
        else:
            bg_hover = self.widget.peng.resourceMgr.normTex(bg_hover, "gui")
            assert bg_hover[1] == self.bg_texinfo[1]  # see init_bg()
            self.bg_hover=bg_hover
        if bg_disabled is None:
            self.bg_disabled=bg
        else:
            bg_disabled = self.widget.peng.resourceMgr.normTex(bg_disabled, "gui")
            assert bg_disabled[1] == self.bg_texinfo[1]  # see init_bg()
            self.bg_disabled=bg_disabled
        if bg_pressed is None:
            self.bg_pressed=bg
        else:
            bg_pressed = self.widget.peng.resourceMgr.normTex(bg_pressed, "gui")
            assert bg_pressed[1] == self.bg_texinfo[1]  # see init_bg()
            self.bg_pressed=bg_pressed
        super(ImageBackground,self).__init__(widget)
    def init_bg(self):
        # TODO: add seperate groups per active texture, in case the different images are on different textures
        self.bg_group = pyglet.graphics.TextureGroup(_FakeTexture(*self.bg_texinfo), parent=pyglet.graphics.OrderedGroup(self.vlist_layer))
        self.vlist_bg = self.submenu.batch2d.add(4,GL_QUADS,self.bg_group,
            "v2f",
            ("t3f",self.bg_texinfo[2]),
            )
        self.reg_vlist(self.vlist_bg)
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
        elif self.pressed:
            self.vlist_bg.tex_coords = self.bg_pressed[2]
        elif self.widget.is_hovering:
            self.vlist_bg.tex_coords = self.bg_hover[2]
        else:
            self.vlist_bg.tex_coords = self.bg_texinfo[2]

    @property
    def pressed(self):
        """
        Read-only helper property to be used by borderstyles for determining if the widget should be rendered as pressed or not.

        Note that this property may not represent the actual pressed state, it will always be False if ``change_on_press`` is disabled.
        """
        return self.change_on_press and (self.widget.pressed or getattr(self.widget, "focussed", False))

class ImageButton(Button):
    """
    Subclass of :py:class:`Button` using an image as a background instead.
    
    By default, this Widget uses :py:class:`ImageBackground` as its Background class.
    
    There are no changes to any other mechanics of the Button, only visually.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=None,bg=None,
                 label="Button",
                 font_size=None, font=None,
                 font_color=None,
                 bg_idle=None,
                 bg_hover=None,
                 bg_disabled=None,
                 bg_pressed=None,
                 label_layer=1,
                 ):
        font = font if font is not None else submenu.font
        font_size = font_size if font_size is not None else submenu.font_size
        font_color = font_color if font_color is not None else submenu.font_color

        if bg is None:
            self.peng = peng
            bg = ImageBackground(self,bg_idle,bg_hover,bg_disabled,bg_pressed)
        super(ImageButton,self).__init__(name,submenu,window,peng,pos,size,bg,label=label, font_size=font_size, font_color=font_color, font=font, label_layer=label_layer)


class FramedImageBackground(ImageBackground):
    """
    Background for the :py:class:`FramedImageButton` Widget.

    This background is similar to :py:class:`ImageBackground`\\ , but it attempts to scale smarter with less artifacts.
    """
    def __init__(self,widget,
                 bg_idle=None,
                 bg_hover=None,
                 bg_disabled=None,
                 bg_pressed=None,
                 frame=[[2,10,2],[2,10,2]],
                 scale=(0, 0),
                 repeat_edge=False,
                 repeat_center=False,
                 tex_size=None,
                 ):
        super(FramedImageBackground, self).__init__(widget, bg_idle, bg_hover, bg_disabled, bg_pressed)

        if tex_size is None:
            if (not (isinstance(bg_idle, list) or isinstance(bg_idle, tuple))) and len(bg_idle) != 2:
                raise TypeError("Invalid type or length of bg_idle for auto-tex_size, please specify tex_size")
            self.tsx, self.tsy = self.widget.peng.resourceMgr.getTexSize(bg_idle[0], bg_idle[1])  # Texture Size in pixels
        else:
            self.tsx, self.tsy = tex_size
        self.frame_x = list(
            map(lambda x: x * (self.tsx / sum(frame[0])), frame[0]))  # Frame Size in the texture, in pixels
        self.frame_y = list(map(lambda y: y * (self.tsy / sum(frame[1])), frame[1]))

        self._scale = scale

        self.repeat_edge = repeat_edge
        self.repeat_center = repeat_center

        for i in frame:
            if (self.repeat_edge or self.repeat_center) and i[1] == 0:
                raise ValueError("Cannot repeat edges or center with the middle frame being 0")

    @property
    def scale(self):
        if self._scale == (None, None):
            raise ValueError(f"Scale cannot be {self._scale}")

        scale = self._scale
        if scale[0] == 0:  # 0 makes the resulting frames similar to the texture frames but scaled up to the widget size
            scale = self.widget.size[0] / sum(self.frame_x), scale[1]
        if scale[1] == 0:
            scale = scale[0], self.widget.size[1] / sum(self.frame_y)
        if scale[0] == None:  # None makes the scale similar to the second scale
            scale = scale[1], scale[1]
        if scale[1] == None:
            scale = scale[0], scale[0]
        return scale

    def init_bg(self):
        if (self.frame_x[0] + self.frame_x[2]) * self.scale[0] > self.widget.size[0] or \
                (self.frame_y[0] + self.frame_y[2]) * self.scale[1] > self.widget.size[1]:
            raise ValueError(f"Scale {self.scale} is too large for this widget")

        self.bg_group = pyglet.graphics.TextureGroup(_FakeTexture(*self.bg_texinfo),
                                                     parent=pyglet.graphics.OrderedGroup(self.vlist_layer))
        self.vlist_corners = self.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_edges = self.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_center = self.submenu.batch2d.add(4, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.reg_vlist(self.vlist_corners)
        self.reg_vlist(self.vlist_edges)
        self.reg_vlist(self.vlist_center)

    def redraw_bg(self):
        # Convenience Variables
        sx, sy = self.widget.size
        x, y = self.widget.pos

        # Frame length in the result, in pixels
        flx, fcx, frx = map(lambda x: self.scale[0] * x, self.frame_x)
        sfcx = sx - (flx + frx)  # Stretched center frame length
        fdy, fcy, fuy = map(lambda y: self.scale[1] * y, self.frame_y)
        sfcy = sy - (fdy + fuy)

        amx, amy, rx, ry = 0, 0, 0, 0
        if self.repeat_center or self.repeat_edge:
            amx, amy = int(sfcx / fcx), int(sfcy / fcy)  # Amount of complete textures in an edge
            rx, ry = sfcx % fcx, sfcy % fcy  # Length of the rest tile in pixels

        # Vertices

        # 11-10---15-14
        # |   |   |   |
        # 8---9---12-13
        # |   |   |   |
        # 3---2---7---6
        # |   |   |   |
        # 0---1---4---5

        # Corners
        #     x         y
        v0 = x, y
        v1 = x + flx, y
        v2 = x + flx, y + fdy
        v3 = x, y + fdy

        v4 = x + sx - frx, y
        v5 = x + sx, y
        v6 = x + sx, y + fdy
        v7 = x + sx - frx, y + fdy

        v8 = x, y + sy - fuy
        v9 = x + flx, y + sy - fuy
        v10 = x + flx, y + sy
        v11 = x, y + sy

        v12 = x + sx - frx, y + sy - fuy
        v13 = x + sx, y + sy - fuy
        v14 = x + sx, y + sy
        v15 = x + sx - frx, y + sy

        self.vlist_corners.vertices = v0 + v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8 + v9 + v10 + v11 + v12 + v13 + v14 + v15

        if self.repeat_edge:
            self.vlist_edges.resize(8 * (amx + amy + 2))

            vd, vu, vl, vr = [], [], [], []
            for i in range(amx):
                vd += x + flx + i * fcx, y
                vd += x + flx + (i + 1) * fcx, y
                vd += x + flx + (i + 1) * fcx, y + fdy
                vd += x + flx + i * fcx, y + fdy

                vu += x + flx + i * fcx, y + sy - fuy
                vu += x + flx + (i + 1) * fcx, y + sy - fuy
                vu += x + flx + (i + 1) * fcx, y + sy
                vu += x + flx + i * fcx, y + sy

            vd += x + sx - frx - rx, y
            vd += x + sx - frx, y
            vd += x + sx - frx, y + fdy
            vd += x + sx - frx - rx, y + fdy

            vu += x + sx - frx - rx, y + sy - fuy
            vu += x + sx - frx, y + sy - fuy
            vu += x + sx - frx, y + sy
            vu += x + sx - frx - rx, y + sy

            for j in range(amy):
                vl += x, y + fdy + j * fcy
                vl += x + flx, y + fdy + j * fcy
                vl += x + flx, y + fdy + (j + 1) * fcy
                vl += x, y + fdy + (j + 1) * fcy

                vr += x + sx - frx, y + fdy + j * fcy
                vr += x + sx, y + fdy + j * fcy
                vr += x + sx, y + fdy + (j + 1) * fcy
                vr += x + sx - frx, y + fdy + (j + 1) * fcy

            vl += x, y + sy - fuy - ry
            vl += x + flx, y + sy - fuy - ry
            vl += x + flx, y + sy - fuy
            vl += x, y + sy - fuy

            vr += x + sx - frx, y + sy - fuy - ry
            vr += x + sx, y + sy - fuy - ry
            vr += x + sx, y + sy - fuy
            vr += x + sx - frx, y + sy - fuy

            self.vlist_edges.vertices = vd + vl + vr + vu
        else:
            self.vlist_edges.vertices = v1 + v4 + v7 + v2 + v3 + v2 + v9 + v8 + v7 + v6 + v13 + v12 + v9 + v12 + v15 + v10

        if self.repeat_center:
            self.vlist_center.resize(4 * (amx + 1) * (amy + 1))
            v = []

            # Completed tiles
            for j in range(amy):
                for i in range(amx):
                    v += x + flx + i * fcx, y + fdy + j * fcy
                    v += x + flx + (i + 1) * fcx, y + fdy + j * fcy
                    v += x + flx + (i + 1) * fcx, y + fdy + (j + 1) * fcy
                    v += x + flx + i * fcx, y + fdy + (j + 1) * fcy

            # X-shortened tiles
            for j in range(amy):
                v += x + sx - frx - rx, y + fdy + j * fcy
                v += x + sx - frx, y + fdy + j * fcy
                v += x + sx - frx, y + fdy + (j + 1) * fcy
                v += x + sx - frx - rx, y + fdy + (j + 1) * fcy

            # Y-shortened tiles
            for i in range(amx):
                v += x + flx + i * fcx, y + sy - fuy - ry
                v += x + flx + (i + 1) * fcx, y + sy - fuy - ry
                v += x + flx + (i + 1) * fcx, y + sy - fuy
                v += x + flx + i * fcx, y + sy - fuy

            # X-Y-shortened tile
            v += x + sx - frx - rx, y + sy - fuy - ry
            v += x + sx - frx, y + sy - fuy - ry
            v += x + sx - frx, y + sy - fuy
            v += x + sx - frx - rx, y + sy - fuy

            self.vlist_center.vertices = v
        else:
            self.vlist_center.vertices = v2 + v7 + v12 + v9

        if not self.widget.enabled:
            self.vlist_corners.tex_coords, self.vlist_edges.tex_coords, self.vlist_center.tex_coords = self.transform_texture(
                self.bg_disabled, amx, amy, rx, ry
            )
        elif self.pressed:
            self.vlist_corners.tex_coords, self.vlist_edges.tex_coords, self.vlist_center.tex_coords = self.transform_texture(
                self.bg_pressed, amx, amy, rx, ry
            )
        elif self.widget.is_hovering:
            self.vlist_corners.tex_coords, self.vlist_edges.tex_coords, self.vlist_center.tex_coords = self.transform_texture(
                self.bg_hover, amx, amy, rx, ry
            )
        else:
            self.vlist_corners.tex_coords, self.vlist_edges.tex_coords, self.vlist_center.tex_coords = self.transform_texture(
                self.bg_texinfo, amx, amy, rx, ry
            )

    def transform_texture(self, texture, amx, amy, rx, ry):
        t = texture[2]
        sx, sy = self.widget.size

        tx, ty = t[3] - t[0], t[10] - t[1]  # Texture Size on texture level

        # Frame length on texture level
        flx, fcx, frx = map(lambda x: x * tx / self.tsx, self.frame_x)
        fdy, fcy, fuy = map(lambda y: y * ty / self.tsy, self.frame_y)

        if self.repeat_center or self.repeat_edge:
            rx = (rx * tx) / (self.tsx * self.scale[0])
            ry *= ty / self.tsy / self.scale[1]

        t0 = t[0], t[1], t[2]
        t1 = t[0] + flx, t[1], t[2]
        t2 = t[0] + flx, t[1] + fdy, t[2]
        t3 = t[0], t[1] + fdy, t[2]

        t4 = t[3] - frx, t[4], t[5]
        t5 = t[3], t[4], t[5]
        t6 = t[3], t[4] + fdy, t[5]
        t7 = t[3] - frx, t[4] + fdy, t[5]

        t8 = t[9], t[10] - fuy, t[11]
        t9 = t[9] + flx, t[10] - fuy, t[11]
        t10 = t[9] + flx, t[10], t[11]
        t11 = t[9], t[10], t[11]

        t12 = t[6] - frx, t[7] - fuy, t[8]
        t13 = t[6], t[7] - fuy, t[8]
        t14 = t[6], t[7], t[8]
        t15 = t[6] - frx, t[7], t[8]

        corner_tex = t0 + t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11 + t12 + t13 + t14 + t15

        if self.repeat_edge:
            td, tl, tr, tu = [], [], [], []

            td += (t1 + t4 + t7 + t2) * amx
            tu += (t9 + t12 + t15 + t10) * amx

            td += t1
            td += t[0] + flx + rx, t[1], t[2]
            td += t[0] + flx + rx, t[1] + fdy, t[2]
            td += t2

            tu += t9
            tu += t[9] + flx + rx, t[10] - fuy, t[11]
            tu += t[9] + flx + rx, t[10], t[11]
            tu += t10

            tl += (t3 + t2 + t9 + t8) * amy
            tr += (t7 + t6 + t13 + t12) * amy

            tl += t3 + t2
            tl += t[0] + flx, t[1] + fdy + ry, t[2]
            tl += t[0], t[1] + fdy + ry, t[2]

            tr += t7 + t6
            tr += t[3], t[4] + fdy + ry, t[5]
            tr += t[3] - frx, t[4] + fdy + ry, t[5]

            edge_tex = td + tl + tr + tu
        else:
            edge_tex = t1 + t4 + t7 + t2 + t3 + t2 + t9 + t8 + t7 + t6 + t13 + t12 + t9 + t12 + t15 + t10

        if self.repeat_center:
            tc = []

            tc += (t2 + t7 + t12 + t9) * amx * amy
            for i in range(amy):
                tc += t2
                tc += t[0] + flx + rx, t[1] + fdy, t[2]
                tc += t[9] + flx + rx, t[10] - fuy, t[11]
                tc += t9

            for i in range(amx):
                tc += t2 + t7
                tc += t[3] - frx, t[4] + fdy + ry, t[5]
                tc += t[0] + flx, t[1] + fdy + ry, t[2]

            tc += t2
            tc += t[0] + flx + rx, t[1] + fdy, t[2]
            tc += t[0] + flx + rx, t[1] + fdy + ry, t[8]
            tc += t[0] + flx, t[1] + fdy + ry, t[2]

            center_tex = tc
        else:
            center_tex = t2 + t7 + t12 + t9

        return corner_tex, edge_tex, center_tex

class FramedImageButton(ImageButton):
    """
    Subclass of :py:class:`ImageButton` adding smart scaling to the background.

    By default, this Widget uses :py:class:`FramedImageBackground` as its Background class.

    ``frame`` defines the ratio between the borders and the center. The sum of each item must
    be greater than zero, else a ZeroDivisionError may be thrown. Note that up to two items
    of each frame may be left as ``0``\ . This will cause the appropriate border or center
    to not be rendered at all.

    ``tex_size`` may be left empty if a resource name is passed. It will then be automatically
    determined.

    .. todo::
        Document ``scale``
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None, size=None,bg=None,
                 label="Button",
                 font_size=None, font=None,
                 font_color=None,
                 bg_idle=None,
                 bg_hover=None,
                 bg_disabled=None,
                 bg_pressed=None,
                 frame=[[2,10,2],[2,10,2]],
                 scale=(1, 1),
                 repeat_edge=False,
                 repeat_center=False,
                 tex_size=None,
                 label_layer=1,
                 ):
        font = font if font is not None else submenu.font
        font_size = font_size if font_size is not None else submenu.font_size
        font_color = font_color if font_color is not None else submenu.font_color

        if bg is None:
            self.peng = peng
            bg = FramedImageBackground(self,bg_idle,bg_hover,bg_disabled,bg_pressed,frame, scale, repeat_edge, repeat_center, tex_size)
        super(FramedImageButton,self).__init__(name,submenu,window,peng,pos=pos,size=size,bg=bg,label=label, font_size=font_size, font_color=font_color, font=font, label_layer=label_layer)


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
    vlist_layer = 1
    
    def __init__(self,widget,borderstyle,checkcolor=[240,119,70],**kwargs):
        self.checkcolor = checkcolor
        super(CheckboxBackground,self).__init__(widget,[3,3],borderstyle,**kwargs)
    def init_bg(self):
        super(CheckboxBackground,self).init_bg()
        self.vlist_check = self.submenu.batch2d.add(4,GL_QUADS,pyglet.graphics.OrderedGroup(10),
            "v2f",
            "c3B",
            )
        self.reg_vlist(self.vlist_check)
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
                 pos=None, size=None,bg=None,
                 borderstyle=None,
                 label="Checkbox",
                 checkcolor=[240,119,70],
                 font_size=None, font=None,
                 font_color=None,
                 label_layer=1,
                 ):
        font = font if font is not None else submenu.font
        font_size = font_size if font_size is not None else submenu.font_size
        font_color = font_color if font_color is not None else submenu.font_color
        borderstyle = borderstyle if borderstyle is not None else submenu.borderstyle

        if bg is None:
            bg = CheckboxBackground(self,borderstyle,checkcolor)
        super(Checkbox,self).__init__(name,submenu,window,peng,pos,size,bg,borderstyle=borderstyle,label=label, font_size=font_size, font_color=font_color, font=font, label_layer=label_layer)
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
