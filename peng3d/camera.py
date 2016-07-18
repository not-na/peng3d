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
    """
    Camera object representing a location to draw from.
    
    Each :py:class:`Camera` object is bound to a world and has three properties: a name, :py:attr:`pos` and :py:attr:`rot`\ .
    
    The name of the camera can be any string and is used to identify the camera and thus should be unique.
    """
    def __init__(self,world,name,pos=None,rot=None):
        if not (isinstance(name,str) or isinstance(name,bytes) or isinstance(unicode)):
            raise TypeError("name must be an instance of basestring!")
        self.world = world
        self._pos = pos if pos is not None else [0,0,0]
        self._rot = rot if rot is not None else [0,0]
        self.name = name
    
    def on_activate(self,old):
        """
        Fake event handler called when this camera is made current by a :py:class:`WorldView()` object.
        """
        pass
    def on_rotate(self,old,new):
        """
        Fake event handler called when this camera is rotated.
        
        The ``old`` and ``new`` parameters are both rotations and are not equal. Each parameter is a 2-tuple of ``(yaw,pitch)``\ .
        """
        pass
    def on_move(self,old,new):
        """
        Fake event handler called when this camera moves.
        
        The ``old`` and ``new`` parameters are both 3D Locations and are not equal. Each parameter is a 3-tuple of ``(x,y,z)`` in world coordinates.
        """
        pass
    
    # Move/Rotate methods
    
    @property
    def pos(self):
        """
        Property for accessing the position of the camera.
        
        This property uses a setter to call the :py:meth:`on_move()` method if set and the new location is not equal to the old location.
        """
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
        """
        Property for accessing the rotation of the camera.
        
        This property uses a setter to call the :py:meth:`on_rotate()` method if set and the new location is not equal to the old location.
        """
        return self._rot
    @rot.setter
    def rot(self,value):
        if self._rot == value:
            return # Rotation unchanged
        old = self._rot
        self._rot = value
        self.on_rotate(old,value)

class CameraActorFollower(Camera):
    """
    Special Camera that follows the specified :py:class:`Actor()`\ .
    
    Note that neither the :py:meth:`on_move() <Camera.on_move>` nor the :py:meth:`on_rotate() <Camera.on_rotate>` event handlers are called due to the way the updating works.
    """
    def __init__(self,world,name,actor):
        super(CameraActorFollower,self).__init__(world,name)
        del self._pos,self._rot
        self.actor = actor
    
    @property
    def pos(self):
        """
        This property always equals the value of ``self.actor.pos``\ .
        
        This property may also be written to.
        """
        return self.actor.pos
    @pos.setter
    def pos(self,value):
        self.actor.pos = value
    
    @property
    def rot(self):
        """
        This property always equals the value of ``self.actor.rot``\ .
        
        This property may also be written to.
        """
        return self.actor.rot
    @rot.setter
    def rot(self,value):
        self.actor.rot = value
