#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui.py
#  
#  Copyright 2017 notna <notna@apparat.org>
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
    "mouse_aabb",
    "points2htmlfontsize",
    "ResourceGroup",
    "BlitableTexture",
    ]

import pyglet
from pyglet.gl import *

def mouse_aabb(mpos,size,pos):
    """
    AABB Collision checker that can be used for most axis-aligned collisions.
    
    Intended for use in widgets to check if the mouse is within the bounds of a particular widget.
    """
    return pos[0]<=mpos[0]<=pos[0]+size[0] and pos[1]<=mpos[1]<=pos[1]+size[1]

def points2htmlfontsize(points):
    """
    Approximate font size converter, converts from Points to HTML ``<font>`` tag font sizes.
    
    Note that this method is very inaccurate, since there are only seven possible output values that represent at least 25 input values.
    When in doubt, this function always rounds down, e.g. every input value less than eight is converted to HTML size 1.
    """
    # Approximation, always rounds down
    if points<=8:
        return 1
    elif points<=10:
        return 2
    elif points<=12:
        return 3
    elif points<=14:
        return 4
    elif points<=18:
        return 5
    elif points<=24:
        return 6
    else:
        # Inaccurate, represents everything above 24, but should equal 48
        return 7

class ResourceGroup(pyglet.graphics.Group):
    """
    Pyglet Group that represents a Resource as returned by the :py:class:`ResourceManager() <peng3d.resource.ResourceManager>`\\ .
    
    This Group should automatically merge different groups with different resources that are on the same texture atlas.
    """
    def __init__(self,data,parent=None):
        super(ResourceGroup, self).__init__(parent)
        self.data = data

    def set_state(self):
        glEnable(self.data[0])
        glBindTexture(self.data[0], self.data[1])
    set_state.__noautodoc__ = True

    def unset_state(self):
        glDisable(self.data[0])
    unset_state.__noautodoc__ = True

    def __hash__(self):
        return hash((self.data[0], self.data[1], self.parent))

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
            self.data[0] == other.data[0] and
            self.data[1] == other.data[1] and
            self.parent == other.parent)

    def __repr__(self):
        return '%s(id=%d)' % (self.__class__.__name__, self.data[1])

class BlitableTexture(pyglet.image.Texture):
    """
    Texture subclass allowing :py:class:`pyglet.image.atlas.TextureBin()` to copy a texture to itself.
    
    This class simply implements the :py:meth:`blit_to_texture()` interface.
    """
    # Basic Texture subclass allowing pyglet.image.atlas.TextureBin to copy a texture to itself
    def blit_to_texture(self,target,level,x,y,z=0):
        glCopyTexSubImage2D(target, level, x,y, 0,0, self.width,self.height)
