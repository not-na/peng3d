#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  text.py
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
    "Label",
    "TextInput","TextInputBackground"
    ]

import time

import pyglet
from pyglet.gl import *
from pyglet.window import key

try:
    import pyperclip
    HAVE_PYPERCLIP = True
except ImportError:
    HAVE_PYPERCLIP = False

from .widgets import Background,Widget,mouse_aabb
from .button import ButtonBackground


class Label(Widget):
    """
    Simple widget that can display any single-line non-formatted string.
    
    This widget does not use any background by default.
    
    The default font color is chosen to work on the default background color and may need to be changed if the background color is changed.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None,
                 label="Label",
                 font_size=16,font="Arial",
                 font_color=[62,67,73,255],
                 multiline=False,
                 label_cls=pyglet.text.Label,
                ):
        super(Label,self).__init__(name,submenu,window,peng,pos,size,bg)
        
        self.font_name = font
        self.font_size = font_size
        self.font_color = font_color
        
        if label_cls == pyglet.text.HTMLLabel:
            self._label = label_cls(label,
                    # Font is changed later
                    x=0,y=0,
                    batch=self.submenu.batch2d,
                    anchor_x="center", anchor_y="center",
                    group=pyglet.graphics.OrderedGroup(1),
                    width=self.size[0],height=self.size[1],
                    multiline=multiline,
                    )
            self._label.font_name = font
            self._label.font_size = font_size
            self._label.font_color = font_color
        else:
            self._label = label_cls(label,
                    font_name=font,
                    font_size=font_size,
                    color=font_color,
                    x=0,y=0,
                    batch=self.submenu.batch2d,
                    anchor_x="center", anchor_y="center",
                    group=pyglet.graphics.OrderedGroup(1),
                    width=self.size[0],height=self.size[1],
                    multiline=multiline,
                    )
        
        self.redraw()
    
    def on_redraw(self,dt=None):
        super(Label,self).on_redraw()
        self.redraw_label()
    def redraw_label(self):
        """
        Re-draws the text by calculating its position.
        
        Currently, the text will always be centered on the position of the label.
        """
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        
        # Label position
        self._label.font_name = self.font_name
        self._label.font_size = self.font_size
        self._label.font_color = self.font_color
        
        self._label.x = int(x+sx/2.)
        self._label.y = int(y+sy/2.)
        self._label.width = self.size[0]
        self._label.height = self.size[1]
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
    
    @property
    def label(self):
        """
        Property for accessing the text of the label.
        """
        return self._label.text
    @label.setter
    def label(self,label):
        self._label.text = label


class TextInputBackground(ButtonBackground):
    """
    Background for the :py:class:`TextInput` Widget.
    
    This background uses the button drawing routines and adds a cursor.
    """
    def __init__(self,*args,**kwargs):
        self.stime = 0
        super(TextInputBackground,self).__init__(*args,**kwargs)
    def init_bg(self):
        super(TextInputBackground,self).init_bg()
        self.vlist_cursor = self.submenu.batch2d.add(2,GL_LINES,pyglet.graphics.OrderedGroup(10),
            "v2f",
            "c3B",
            )
        self.reg_vlist(self.vlist_cursor)
    def redraw_bg(self):
        super(TextInputBackground,self).redraw_bg()
        
        sx,sy,x,y,bx,by = self.getPosSize()
        
        # TODO: make this less hacky
        otext = self.widget._text.text
        self.widget._text.text = self.widget._text.text[:self.widget.cursor_pos]
        tw = self.widget._text.content_width+2 if len(self.widget._text.text)!=0 else 0
        self.widget._text.text = otext
        
        v = x+tw+bx,y+by, x+tw+bx,y+sy-by
        self.vlist_cursor.vertices = v
        
        bg,o,i,s,h = self.getColors()
        # TODO: add compat with arbitrary backgrounds, will not work on material
        c = s*2 if (self.stime-time.time())%1>.5 or not self.widget.focussed else [0,0,0]*2
        self.vlist_cursor.colors = c
    
    @property
    def pressed(self):
        return self.change_on_press and self.widget.focussed


class TextInput(Widget):
    """
    Basic Textual Input widget.
    
    By default, this widget uses :py:class:`TextInputBackground` as its Background class.
    
    The optional default text will only be displayed if the text is empty.
    
    The ``allow_overflow`` flag determines if the text entered can be longer than the size of the :py:class:`TextInput`\ .
    
    The ``allow_copypaste`` flag controls whether or not the user can copy and paste the contents of the text box.
    By default, copying and pasting is allowed. This flag can also be set to ``"force"`` to force a crash
    with an appropriate error message if the :py:mod:`pyperclip` module is not available.
    Currently, only copying, pasting and cutting the whole text box is supported, as there is no mechanism for text selection yet.
    
    The key combinations used by this widget can be configured in the config via the :confval:`controls.keybinds.common.*` config values.
    """
    def __init__(self,name,submenu,window,peng,
                 pos=None,size=None,
                 bg=None,
                 text="",default="",
                 border=[4,4],borderstyle="flat",
                 font_size=16,font="Arial",
                 font_color=[62,67,73,255],
                 font_color_default=[62,67,73,200],
                 allow_overflow=False,
                 allow_copypaste=True,
                 ):
        
        if allow_copypaste == "force" and not HAVE_PYPERCLIP:
            raise ValueError("%s with name %s requires Clipboard support, but Pyperclip is not installed"%(self.__class__.__name__,name))
        
        if bg is None:
            bg = TextInputBackground(self,border,borderstyle)
        super(TextInput,self).__init__(name,submenu,window,peng,pos,size,bg)
        
        self.cursor_pos = 0
        self.focussed = False
        self.allow_overflow = allow_overflow
        self.allow_copypaste = True if allow_copypaste is True or allow_copypaste=="force" else False
        self.force_copypaste = True if allow_copypaste=="force" else False
        
        self._text = pyglet.text.Label(text,
                font_name=font,
                font_size=font_size,
                color=font_color,
                x=0,y=0,
                batch=None,#self.submenu.batch2d,
                anchor_x="left", anchor_y="center",
                width=self.size[0],height=self.size[1]
                )
        self._default = pyglet.text.Label(default,
                font_name=font,
                font_size=font_size,
                color=font_color_default,
                x=0,y=0,
                batch=None,
                anchor_x="left", anchor_y="center",
                width=self.size[0],height=self.size[1]
                )
        self.cursor_pos = 0
        self.focussed = False
        
        self.peng.registerEventHandler("on_text",self.on_text)
        self.peng.registerEventHandler("on_text_motion",self.on_text_motion)
        if self.allow_copypaste:
            self.peng.keybinds.add(self.window.cfg["controls.keybinds.common.copy"],"peng3d:gui.widget.textinput.%s.copy"%self.name,self.on_copy)
            self.peng.keybinds.add(self.window.cfg["controls.keybinds.common.paste"],"peng3d:gui.widget.textinput.%s.paste"%self.name,self.on_paste)
            self.peng.keybinds.add(self.window.cfg["controls.keybinds.common.cut"],"peng3d:gui.widget.textinput.%s.cut"%self.name,self.on_cut)
        
        self.redraw()
        pyglet.clock.schedule_interval(lambda dt: self.redraw(),1./2.)
    
    def on_redraw(self):
        super(TextInput,self).on_redraw()
        self.redraw_label()
    def redraw_label(self):
        """
        Re-draws the label by calculating its position.
        
        Currently, the label will always be centered on the position of the label.
        """
        # Convenience variables
        sx,sy = self.size
        x,y = self.pos
        
        # Label position
        x = x+self.bg.border[0]
        y = y+sy/2.-self._text.font_size/4.
        w = self.size[0]
        h = self.size[1]
        
        self._text.x,self._text.y = x,y
        self._text.width,self._text.height=w,h
        
        self._default.x,self._default.y = x,y
        self._default.width,self._default.height=w,h
        
        self._text._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
        self._default._update()
    
    def draw(self):
        super(TextInput,self).draw()
        if self._text.text=="":
            self._default.draw()
        else:
            self._text.draw()
    draw.__noautodoc__ = True
    
    def on_text(self,text):
        if not (self.focussed and self.clickable):
            return
        
        otext = self.text
        t = self.text
        t = t[:self.cursor_pos]+text+t[self.cursor_pos:]
        self.text = t
        self.cursor_pos+=len(self.text)-len(otext)
        self.cursor_pos = min(self.cursor_pos,len(self.text))
        self.redraw()
    
    def on_text_motion(self,motion):
        if not (self.focussed and self.clickable):
            return
        
        if motion == key.MOTION_BACKSPACE:
            l = list(self.text)
            try:
                # Deletes the character in front of the cursor
                del l[self.cursor_pos-1]
            except Exception:
                return
            self.text = "".join(l)
            self.cursor_pos-=1
            self.cursor_pos = max(self.cursor_pos,0)
            self.redraw()
        elif motion == key.MOTION_DELETE:
            l = list(self.text)
            try:
                # Deletes the character after the cursor
                del l[self.cursor_pos]
            except Exception:
                return
            self.text = "".join(l)
            self.redraw()
        elif motion == key.MOTION_LEFT:
            # Moves the cursor to the left one character
            self.cursor_pos-=1
            self.cursor_pos = max(self.cursor_pos,0)
            self.redraw()
        elif motion == key.MOTION_RIGHT:
            # Moves the cursor to the right one character
            self.cursor_pos+=1
            self.cursor_pos = min(self.cursor_pos,len(self.text))
            self.redraw()
        elif motion == key.MOTION_BEGINNING_OF_LINE or motion == key.MOTION_BEGINNING_OF_FILE:
            # Moves the cursor to the beginning
            self.cursor_pos=0
            self.redraw()
        elif motion == key.MOTION_END_OF_LINE or motion == key.MOTION_END_OF_FILE:
            # Moves the cursor to the end
            self.cursor_pos = len(self.text)
            self.redraw()
    
    def on_mouse_press(self,x,y,button,modifiers):
        if not self.clickable:
            return
        elif mouse_aabb([x,y],self.size,self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("press")
                self.pressed = True
                self.focussed = True
                self.bg.stime = time.time()
            elif button == pyglet.window.mouse.RIGHT:
                self.doAction("context")
            self.redraw()
        else:
            self.focussed = False
            self.redraw()
    
    def on_copy(self,symbol,modifiers,release):
        if release:
            return
        
        try:
            pyperclip.copy(self.text)
        except Exception:
            if self.force_copypaste:
                raise
    def on_paste(self,symbol,modifiers,release):
        if release:
            return
        
        try:
            t = pyperclip.paste()
            
            # Tries to copy as much as possible, until it does not fit
            if not self.allow_overflow:
                # TODO: implement more efficient algorithm
                self.text = ""
                for c in t:
                    self.text+=c
            else:
                self.text=t
        except Exception:
            if self.force_copypaste:
                raise
    def on_cut(self,symbol,modifiers,release):
        if release:
            return
        
        try:
            pyperclip.copy(self.text)
            self.text = ""
        except Exception:
            if self.force_copypaste:
                raise
    
    @property
    def text(self):
        """
        Property for accessing the text.
        """
        return self._text.text
    @text.setter
    def text(self,text):
        otext = self._text.text
        self._text.text = text
        self._text._update()
        # Reverts the change if
        # 1. the text length has NOT increased
        # 2. and allow_overflow is False
        # 3. and the text is wider than the widget size minus the border size
        # 4. and the text is not empty
        if len(otext)<len(text) and not self.allow_overflow and self.size[0]-self.bg.border[0]*2<=self._text.content_width if len(self.text)!=0 else 0:
            self._text.text=otext
            self._text._update()
        self.doAction("textchange")
    
    @property
    def default(self):
        """
        Property for accessing the default text.
        """
        return self._default.text
    @default.setter
    def default(self,default):
        self._default.text = default


