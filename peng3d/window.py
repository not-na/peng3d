#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  window.py
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

__all__ = ["PengWindow","CFG_FOG_DEFAULT","CFG_LIGHT_DEFAULT"]

import math

import pyglet
from pyglet.gl import *


CFG_FOG_DEFAULT = {"enable":False}

CFG_LIGHT_DEFAULT = {"enable":False}

class PengWindow(pyglet.window.Window):
    def __init__(self,peng,*args,**kwargs):
        super(PengWindow,self).__init__(*args,**kwargs)
        self.cameras = {}
        self.cam = None
        self.exclusive = False
        self.layers = []
        self.started = False
        self.cfg = {}
        self.thread = threading.Thread(name="Peng3d window thread",target=self.run)
        self.thread.daemon = True
    def setup(self):
        self.cleanConfig()
        
        glClearColor(*self.cfg["clearColor"])
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        
        glShadeModel(GL_SMOOTH)
        
        if self.cfg["fogSettings"]["enable"]:
            self.setupFog()
        if self.cfg["lightSettings"]["enable"]:
            self.setupLight()
    
    def run(self):
        self.setup()
        pyglet.app.run()
    def cleanConfig(self):
        # OpenGL configs
        self.cfg["clearColor"] = self.cfg.get("clearColor",(0.,0.,0.,1.))
        self.cfg["wireframe"] = self.cfg.get("wireframe",False)
        self.cfg["fieldofview"] = self.cfg.get("fieldofview",65.0)
        self.cfg["nearclip"] = self.cfg.get("nearclip",0.1)
        self.cfg["farclip"] = self.cfg.get("farclip",10000) # It's over 9000!
        
        # OpenGL - Fog
        self.cfg["fogSettings"] = self.cfg.get("fogSettings",CFG_FOG_DEFAULT)
        self.cfg["fogSettings"]["enable"] = self.cfg["fogSettings"].get("enable",False)
        if self.cfg["fogSettings"]["enable"]:
            pass
        
        # OpenGL - Light
        self.cfg["lightSettings"] = self.cfg.get("lightSettings",CFG_LIGHT_DEFAULT)
        self.cfg["lightSettings"]["enable"] = self.cfg["lightSettings"].get("enable",False)
        if self.cfg["lightSettings"]["enable"]:
            pass
        
        # Other configs
        
        return
    
    # Various methods
    def addLayer(self,layer,z=-1):
        if z==-1:
            self.layers.append(layer)
        else:
            self.layers.insert(z,layer)
    
    # Event handlers
    def on_draw(self):
        self.clear()
        for layer in self.layers:
            if layer.enabled:
                layer._draw()
    
    # Proxy for self.cam.rotation
    @property
    def rotation(self):
        return self.cam.rotation
    @rotation.setter
    def rotation(self,value):
        self.cam.rotation = value
    
    # Proxy for self.cam.position
    @property
    def position(self):
        return self.cam.position
    @position.setter
    def position(self,value):
        self.cam.position = value
    
    # Utility methods
    
    def set2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        # Light
        
        glDisable(GL_LIGHTING)
        
        # To avoid accidental wireframe GUIs and fonts
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
        
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def set3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        
        # Light
        
        #glEnable(GL_LIGHTING)
        
        if self.cfg["wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cfg["fieldofview"], width / float(height), self.cfg["nearclip"], self.cfg["farclip"]) # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)
