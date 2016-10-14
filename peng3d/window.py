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
import traceback

import pyglet
from pyglet.gl import *
from pyglet.window import key

from . import config, camera


class PengWindow(pyglet.window.Window):
    """
    Main window class for peng3d and subclass of :py:class:`pyglet.window.Window()`\ .
    
    This class should not be instantiated directly, use the :py:meth:`Peng.createWindow()` method.
    """
    
    def __init__(self,peng,*args,**kwargs):
        super(PengWindow,self).__init__(*args,**kwargs)
        self.peng = peng
        
        self.exclusive = False
        self.started = False
        self.exclusive = False
        
        self.menus = {}
        self.activeMenu = None
        
        self.cfg = config.Config({},defaults=peng.cfg)
        self.eventHandlers = {}
        
        self._setup = False
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                return pyglet.event.EVENT_HANDLED
        self.push_handlers(on_key_press) # to stop the auto-exit on escape
    def setup(self):
        """
        Sets up the OpenGL state.
        
        This method should be called once after the config has been created and before the main loop is started.
        You should not need to manually call this method, as it is automatically called by :py:meth:`run()`\ .
        
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
    def setupFog(self):
        fogcfg = self.cfg["graphics.fogSettings"]
        if not fogcfg["enable"]:
            return
        
        glEnable(GL_FOG)
        
        if fogcfg["color"] is None:
            fogcfg["color"] = self.cfg["graphics.clearColor"]
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*fogcfg["color"]))
        # Set the performance hint.
        glHint(GL_FOG_HINT, GL_DONT_CARE) # TODO: add customization, including headless support
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, fogcfg["start"])
        glFogf(GL_FOG_END, fogcfg["end"])
        
    def setupLight(self):
        raise NotImplementedError("Currently not implemented")
    
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
        
        .. versionchanged:: 1.2a1
           
           The push/pop handlers have been deprecated in favor of the new :py:meth:`Menu.on_enter() <peng3d.menu.Menu.on_enter>`\ , :py:meth:`Menu.on_exit() <peng3d.menu.Menu.on_exit>`\ , etc. events.
        """
        if menu not in self.menus:
            raise ValueError("Menu %s does not exist!"%menu)
        elif menu == self.activeMenu:
            return # Ignore double menu activation to prevent bugs in menu initializer
        old = self.activeMenu
        self.activeMenu = menu
        if old is not None:
            self.menus[old].on_exit(menu)
            #self.pop_handlers()
        self.menu.on_enter(old)
        #self.push_handlers(self.menu)
    def addMenu(self,menu):
        """
        Adds a menu to the list of menus.
        """
        # If there is no menu selected currently, this menu will automatically be made active.
        # Add the line above to the docstring if fixed
        self.menus[menu.name]=menu
        #if self.activeMenu is None:
        #    self.changeMenu(menu.name)
        # currently disabled because of a bug with adding layers
    
    # Event handlers
    def on_draw(self):
        """
        Clears the screen and draws the currently active menu.
        """
        self.clear()
        self.menu.draw()
    
    def dispatch_event(self,event_type,*args):
        """
        Internal event handling method.
        
        This method extends the behaviour inherited from :py:meth:`pyglet.window.Window.dispatch_event()` by calling the various :py:meth:`handleEvent()` methods.
        
        By default, :py:meth:`Peng.handleEvent()`\ , :py:meth:`handleEvent()` and :py:meth:`Menu.handleEvent()` are called in this order to handle events.
        
        Note that some events may not be handled by all handlers during early startup.
        """
        super(PengWindow,self).dispatch_event(event_type,*args)
        try:
            p = self.peng
            m = self.menu
        except AttributeError:
            # To prevent early startup errors
            if hasattr(self,"peng") and self.peng.cfg["debug.events.logerr"]:
                print("Error:")
                traceback.print_exc()
            return
        p.handleEvent(event_type,args,self)
        self.handleEvent(event_type,args)
        m.handleEvent(event_type,args)
    
    def handleEvent(self,event_type,args,window=None):
        args = list(args)
        #if window is not None:
        #    args.append(window)
        if event_type in self.eventHandlers:
            for handler in self.eventHandlers[event_type]:
                handler(*args)
    def registerEventHandler(self,event_type,handler):
        if self.peng.cfg["debug.events.register"]:
            print("Registered Event: %s Handler: %s"%(event_type,handler))
        if event_type not in self.eventHandlers:
            self.eventHandlers[event_type]=[]
        self.eventHandlers[event_type].append(handler)
    
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
    
    # Utility methods
    
    def toggle_exclusivity(self,override=None):
        """
        Toggles mouse exclusivity via pyglet's :py:meth:`set_exclusive_mouse()` method.
        
        If ``override`` is given, it will be used instead.
        
        You may also read the current exclusivity state via :py:attr:`exclusive`\ .
        """
        if override is not None:
            new = override
        else:
            new = not self.exclusive
        self.exclusive = new
        self.set_exclusive_mouse(self.exclusive)
    
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
    def set3d(self,cam):
        """
        Configures OpenGL to draw in 3D.
        
        This method also applies the correct rotation and translation as set in the supplied camera ``cam``\ .
        It is discouraged to use :py:func:`glTranslatef()` or :py:func:`glRotatef()` directly as this may cause visual glitches.
        
        If you need to configure any of the standard parameters, see the docs about :doc:`/configoption`\ .
        
        The :confval:`graphics.wireframe` config value can be used to enable a wireframe mode, useful for debugging visual glitches.
        """
        if not isinstance(cam,camera.Camera):
            raise TypeError("cam is not of type Camera!")
        
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
        x, y = cam.rot
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = cam.pos
        glTranslatef(-x, -y, -z)
