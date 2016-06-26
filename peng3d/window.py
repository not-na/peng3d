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

__all__ = ["PengWindow"]

import math

import pyglet
from pyglet.gl import *

from . import config


class PengWindow(pyglet.window.Window):
    """
    Main window class for peng3d and subclass of :py:class:`pyglet.window.Window()`\ .
    
    This class should not be instantiated directly, use the :py:meth:`Peng.createWindow()` method.
    """
    
    def __init__(self,peng,*args,**kwargs):
        super(PengWindow,self).__init__(*args,**kwargs)
        self.cameras = {}
        self.cam = None
        self.exclusive = False
        self.menus = {}
        self.activeMenu = None
        self.started = False
        self.cfg = config.Config({},defaults=peng.cfg)
        self._setup = False
    def setup(self):
        """
        Sets up the OpenGL state.
        
        This method should be called once after the config has been created and before the main loop is started.
        You should not need to manually call this method, as it is automatically called by :py:meth:`cleanConfig()`\ .
        
        Repeatedly calling this method has no effects.
        """
        if self._setup:
            return
        self._setup = True
        
        # Ensures that default values are supplied
        #self.cleanConfig()
        
        # Sets up basic OpenGL state
        glClearColor(*self.cfg["graphics.clearColor"])
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        
        glShadeModel(GL_SMOOTH)
        
        if self.cfg["graphics.fogSettings"]["enable"]:
            self.setupFog()
        if self.cfg["graphics.lightSettings"]["enable"]:
            self.setupLight()
    
    def run(self):
        """
        Runs the application in the current thread.
        
        This method should not be called directly, especially when using multiple windows, use :py:meth:`Peng.run()` instead.
        
        Note that this method is blocking as rendering needs to happen in the main thread.
        It is thus recommendable to run your game logic in another thread that should be started before calling this method.
        """
        self.setup()
        pyglet.app.run() # This currently just calls the basic pyglet main loop, maybe implement custom main loop for more control
    """def cleanConfig(self):
        ########## Reset quotation marks if uncommenting
        Sets default values for various config values.
        
        .. todo::
           
           Use an defaultdict or similiar instead.
        ########## End quotation marks
        # Various default values are set in this method, this should really be replaced with something more easy to use and robust
        # A possible replacement could be a defaultdict or similiar
        # Update: now replaced by :py:class:`Config()`\ .
        
        # OpenGL configs
        self.cfg["graphics.clearColor"] = self.cfg.get("graphics.clearColor",(0.,0.,0.,1.))
        self.cfg["graphics.wireframe"] = self.cfg.get("graphics.wireframe",False)
        self.cfg["graphics.fieldofview"] = self.cfg.get("graphics.fieldofview",65.0)
        self.cfg["graphics.nearclip"] = self.cfg.get("graphics.nearclip",0.1)
        self.cfg["graphics.farclip"] = self.cfg.get("graphics.farclip",10000) # It's over 9000!
        
        # OpenGL - Fog
        self.cfg["graphics.fogSettings"] = self.cfg.get("graphics.fogSettings",CFG_FOG_DEFAULT)
        self.cfg["graphics.fogSettings"]["enable"] = self.cfg["graphics.fogSettings"].get("enable",False)
        if self.cfg["graphics.fogSettings"]["enable"]:
            pass
        
        # OpenGL - Light
        self.cfg["graphics.lightSettings"] = self.cfg.get("graphics.lightSettings",CFG_LIGHT_DEFAULT)
        self.cfg["graphics.lightSettings"]["enable"] = self.cfg["graphics.lightSettings"].get("enable",False)
        if self.cfg["graphics.lightSettings"]["enable"]:
            pass
        
        # Other configs
        
        return
    """
    # Various methods
    def changeMenu(self,menu):
        """
        Changes to the given menu.
        
        ``menu`` must be a valid menu name that is currently known.
        
        This method will also pop any old handlers and push new handlers from the menu object.
        """
        if menu not in self.menus:
            raise ValueError("Menu %s does not exist!"%menu)
        elif menu == self.activeMenu:
            return # Ignore double menu activation to prevent bugs in menu initializer
        old = self.activeMenu
        self.activeMenu = menu
        if old is not None:
            self.menus[old].on_exit()
            self.pop_handlers()
        self.menu.on_enter(old)
        self.push_handlers(self.menu)
    def addMenu(self,menu):
        """
        Adds a menu to the list of menus.
        
        If there is no menu selected currently, this menu will automatically be made active.
        """
        self.menus[menu.name]=menu
        if self.activeMenu is None:
            self.changeMenu(menu.name)
    
    # Event handlers
    def on_draw(self):
        # Not documented
        # This just draws the appropriate menu
        self.clear()
        self.menu.draw()
    
    def on_key_press(self,symbol,modifiers):
        return True
    
    # Properties/Proxies for various things
    
    # Proxy for self.menus[self.activeMenu]
    @property
    def menu(self):
        """
        Property for accessing the currently active menu.
        
        Always equals ``self.menus[self.activeMenu]``\ .
        
        This property is read-only.
        """
        return self.menus[self.activeMenu]
    
    # Proxy for self.cam.rotation
    @property
    def rotation(self):
        """
        Property for accessing the current rotation of the active camera.
        
        This property can also be written to.
        """
        return self.cam.rotation
    @rotation.setter
    def rotation(self,value):
        self.cam.rotation = value
    
    # Proxy for self.cam.position
    @property
    def position(self):
        """
        Property for accessing the current position of the active camera.
        
        This property can also be written to.
        """
        return self.cam.position
    @position.setter
    def position(self,value):
        self.cam.position = value
    
    # Utility methods
    
    def set2d(self):
        """
        Configures OpenGL to draw in 2D.
        
        Note that wireframe mode is always disabled in 2D-Mode, but can be re-enabled by calling ``glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)``\ .
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
        """
        Configures OpenGL to draw in 3D.
        
        This method also applies the correct rotation and translation as set in the current camera.
        It is discouraged to use :py:func:`glTranslatef()` or :py:func:`glRotatef()` directly as this may cause visual glitches.
        
        If you need to configure any of the standard parameters, see the docs about :doc:`/configoption`\ .
        
        The :confval:`graphics.wireframe` config value can be used to enable a wireframe mode, useful for debugging visual glitches.
        """
        
        # Light
        
        #glEnable(GL_LIGHTING)
        
        if self.cfg["graphics.wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cfg["graphics.fieldofview"], width / float(height), self.cfg["graphics.nearclip"], self.cfg["graphics.farclip"]) # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)
