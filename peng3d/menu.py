#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  menu.py
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

class BasicMenu(object):
    def __init__(self,name,window,peng):
        self.name = name
        self.window = window
        self.peng = peng
    def draw(self):
        pass
    
    # Event handlers
    def on_enter(self,old):
        pass # Custom fake event handler for entering the menu

class Menu(BasicMenu):
    def __init__(self,name,window,peng):
        super(Menu,self).__init__(name,window,peng)
        self.layers = []
    def addLayer(self,layer,z=-1):
        # Adds a new layer to the stack, optionally at the specified z-value
        # The z-value is the index this layer should be inserted in, or -1 for appending
        if z==-1:
            self.layers.append(layer)
        else:
            self.layers.insert(z,layer)
    def draw(self):
        # Draws each layer in the given order
        for layer in self.layers:
            if layer.enabled:
                layer._draw()
