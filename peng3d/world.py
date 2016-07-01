#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  world.py
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

__all__ = ["World","StaticWorld",
           "WorldView", "WorldViewMouseRotatable"]

from .camera import Camera

from pyglet.gl import *

class World(object):
    def __init__(self,peng):
        self.peng = peng
        self.cameras = {}
        self.actors = {}
        self.views = {}
    
    def addCamera(self,camera):
        if not isinstance(camera,Camera):
            raise TypeError("camera is not of type Camera!")
        self.cameras[camera.name]=camera
    def addView(self,view):
        if not isinstance(view,WorldView):
            raise TypeError("view is not of type WorldView!")
        self.views[view.name]=view
    
    def getView(self,name):
        if name not in self.views:
            raise ValueError("Unknown world view")
        return self.views[name]
    
    def render3d(self,view=None):
        pass

class StaticWorld(World):
    def __init__(self,peng,quads,colors):
        super(StaticWorld,self).__init__(peng)
        self.batch3d = pyglet.graphics.Batch()
        self.terrain = self.batch3d.add(len(quads)/3, GL_QUADS, None,
            ("v3f/static",quads),
            ("c3B/static",colors),
            )
    def render3d(self,view=None):
        self.batch3d.draw()

class WorldView(object):
    def __init__(self,world,name,cam):
        self.world = world
        self.name = name
        self.activeCamera = cam
    
    def setActiveCamera(self,name):
        if name == self.activeCamera:
            return # Cam is already active
        if name not in self.world.cameras:
            raise ValueError("Unknown camera name")
        old = self.activeCamera
        self.activeCamera = name
        self.cam.on_activate(old)
    
    # Event handlers
    
    def on_menu_enter(self,old):
        self.world.peng.window.push_handlers(self)
    def on_menu_exit(self,new):
        self.world.peng.window.pop_handlers()
    
    # Proxy for self.cameras[self.activeCamera]
    @property
    def cam(self):
        """
        Property for getting the currently active camera.
        
        Equals ``self.cameras[self.activeCamera]``\ .
        """
        return self.world.cameras[self.activeCamera]
    
    # Proxy for self.cam.rot
    @property
    def rot(self):
        """
        Property for accessing the current rotation of the active camera.
        
        This property can also be written to.
        """
        return self.world.cameras[self.activeCamera].rot
    @rot.setter
    def rot(self,value):
        if not (isinstance(value,list) or isinstance(value,tuple)):
            raise TypeError("Invalid type for rot value!")
        self.world.cameras[self.activeCamera].rot = value
    
    # Proxy for self.cam.pos
    @property
    def pos(self):
        """
        Property for accessing the current position of the active camera.
        
        The value of this property always will be a list of length 3.
        
        This property can also be written to.
        """
        return self.world.cameras[self.activeCamera].pos
    @pos.setter
    def pos(self,value):
        if not (isinstance(value,list) or isinstance(value,tuple)):
            raise TypeError("pos must be list or tuple")
        elif len(value)!=3:
            raise ValueError("pos must be of len 3 not len %s"%len(value))
        self.world.cameras[self.activeCamera].pos = list(value)

class WorldViewMouseRotatable(WorldView):
    def on_menu_enter(self,old):
        super(WorldViewMouseRotatable,self).on_menu_enter(old)
        self.world.peng.window.toggle_exclusivity(True)
    def on_menu_exit(self,new):
        super(WorldViewMouseRotatable,self).on_menu_exit(new)
        self.world.peng.window.toggle_exclusivity(False)
    def on_key_press(self,symbol,modifiers):
        self.world.peng.window.toggle_exclusivity()
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.world.peng.window.exclusive:
            return
        m = 0.15
        x, y = self.rot
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        x %= 360
        newrot = (x,y)
        self.rot= newrot
    def on_mouse_drag(self,x,y,dx,dy,buttons,modifiers):
        self.on_mouse_motion(x,y,dx,dy)
