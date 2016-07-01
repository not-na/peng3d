#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera.py
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

__all__ = ["Camera","CameraActorFollower"]

class Camera(object):
    def __init__(self,world,name,pos=None,rot=None):
        self.world = world
        self._pos = pos if pos is not None else [0,0,0]
        self._rot = rot if rot is not None else [0,0]
        self.name = name
    
    def on_activate(self,old):
        pass
    def on_rotate(self,old,new):
        pass
    def on_move(self,old,new):
        pass
    
    # Move/Rotate methods
    
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        if self._pos == value:
            return # Position unchanged
        old = self._pos
        self._pos = value
        self.on_move(old,value)
    
    @property
    def rot(self):
        return self._rot
    @rot.setter
    def rot(self,value):
        if self._rot == value:
            return # Rotation unchanged
        old = self._rot
        self._rot = value
        self.on_rotate(old,value)

class CameraActorFollower(Camera):
    def __init__(self,world,name,actor):
        super(CameraActorFollower,self).__init__(world,name)
        del self._pos,self._rot
        self.actor = actor
    
    @property
    def pos(self):
        return self.actor.pos
    @pos.setter
    def pos(self,value):
        self.actor.pos = value
    
    @property
    def rot(self):
        return self.actor.rot
    @rot.setter
    def rot(self,value):
        self.actor.rot = value
