#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

__all__ = ["Actor","RotatableActor"]

import uuid as uuidm

class Actor(object):
    def __init__(self,peng,world,uuid,pos=[0,0,0]):
        self.peng = peng
        self.world = world
        self.uuid = uuid if uuid is not None else uuidm.uuid4()
        
        self._pos = pos
    
    # Event handlers
    
    def on_move(self,old):
        pass
    
    # Properties
    
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        old = self._pos
        self._pos = value
        self.on_move(old)

class RotatableActor(Actor):
    def __init__(self,peng,world,uuid=None,pos=[0,0,0],rot=[0,0]):
        super(RotatableActor,self).__init__(peng,world,uuid,pos)
        self._rot = rot
    def move(self,dist):
        x, y = self._rot
        y_angle = math.radians(y)
        x_angle = math.radians(x)
        m = math.cos(y_angle)
        dy = math.sin(y_angle)
        dy = 0.0
        dx = math.cos(x_angle)
        dz = math.sin(x_angle)
        dx,dy,dz = dx*dist,dy*dist,dz*dist
        x,y,z = self._pos
        self.pos = x+dx,y+dy,z+dz
        return dx,dy,dz
    
    # Event handlers
    
    def on_rotate(self,old):
        pass
    
    # Properties
    
    @property
    def rot(self):
        return self._rot
    @rot.setter
    def rot(self,value):
        old = self._rot
        self._rot = value
        self.on_rotate(old)
