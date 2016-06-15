#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  layer.py
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

__all__ = ["Layer", "Layer2D", "Layer3D"]

class Layer(object):
    def __init__(self,window,peng):
        self.window = window
        self.peng = peng
        self.enabled = True
    # Subclass overrides
    def draw(self):
        """Override in subclasses to define functionality."""
        pass
    def predraw(self):
        pass
    def postdraw(self):
        pass
    # End subclass overrides
    def _draw(self):
        self.predraw()
        self.draw()
        self.postdraw()

class Layer2D(Layer):
    def predraw(self):
        self.window.set2d()

class Layer3D(Layer):
    def predraw(self):
        self.window.set3d()
