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

try:
    import pyglet
    from pyglet.gl import *
    from pyglet.window import key
    _have_pyglet = True
except ImportError:
    _have_pyglet = False

class World(object):
    """
    World containing terrain, actors, cameras and views.
    
    See the docs about :py:class:`Camera()`\ , :py:class:`WorldView()`\ , :py:class:`Actor()` for more information about each class.
    
    This class does not draw anything, see :py:class:`StaticWorld()` for drawing simple terrain.
    """
    def __init__(self,peng):
        self.peng = peng
        self.cameras = {}
        self.actors = {}
        self.views = {}
        
        self.eventHandlers = {}
        self.recvEvents = True
    
    def addCamera(self,camera):
        """
        Add the camera to the internal registry.
        
        Each camera name must be unique, or else only the most recent version will be used. This behaviour should not be relied on because some objects may cache objects.
        
        Additionally, only instances of :py:class:`Camera() <peng3d.camera.Camera>` may be used, everything else raises a :py:exc:`TypeError`\ .
        """
        if not isinstance(camera,Camera):
            raise TypeError("camera is not of type Camera!")
        self.cameras[camera.name]=camera
    def addView(self,view):
        """
        Adds the supplied :py:class:`WorldView()` object to the internal registry.
        
        The same restrictions as for cameras apply, e.g. no duplicate names.
        
        Additionally, only instances of :py:class:`WorldView()` may be used, everything else raises a :py:exc:`TypeError`\ .
        """
        if not isinstance(view,WorldView):
            raise TypeError("view is not of type WorldView!")
        self.views[view.name]=view
    def addActor(self,actor):
        """
        Adds the given actor to the internal registry.
        
        Note that this actors :py:attr:`uuid` attribute must be unique, else it will override any actors previously registered with its UUID.
        """
        self.actors[actor.uuid]=actor
    
    def getView(self,name):
        """
        Returns the view with name ``name``\ .
        
        Raises a :py:exc:`ValueError` if the view does not exist.
        """
        if name not in self.views:
            raise ValueError("Unknown world view")
        return self.views[name]
    
    def render3d(self,view=None):
        """
        Renders the world in 3d-mode.
        
        If you want to render custom terrain, you may override this method. Be careful that you still call the original method or else actors may not be rendered.
        """
        pass
    
    # Event Handlers
    def handle_event(self,event_type,args,window=None):
        if not self.recvEvents:
            if self.peng.cfg["debug.events.dump"]:
                print("World skyps event type %s"%event_type)
            return
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

class StaticWorld(World):
    """
    Subclass of :py:class:`StaticWorld()`\ , allows for semi-static terrain to be rendered.
    
    This class is not suitable for highly complex or user-modifiable terrain.
    
    ``quads`` is a list of 3d vertices, e.g. a single quad may be ``[-1,-1,-1, 1,-1,-1, 1,-1,1, -1,-1,1]``\ , which represents a rectangle of size 2x2 centered around 0,0.
    It should also be noted that all quads have to be in a single list.
    
    ``colors`` is a list of RGB Colors in a similiar format to ``quads`` but with colors instead. Note that there must be a color for every vertex in the vertice list.
    Every color is an integer between 0 and 255 using the internal pyglet scheme ``c3B/static``\ .
    
    You can modify the terrain via the ``terrain`` attribute, note that it is a pyglet vertex list, and not a python list.
    """
    def __init__(self,peng,quads,colors):
        super(StaticWorld,self).__init__(peng)
        assert _have_pyglet
        self.batch3d = pyglet.graphics.Batch()
        self.terrain = self.batch3d.add(len(quads)/3, GL_QUADS, None,
            ("v3f/static",quads),
            ("c3B/static",colors),
            )
    def render3d(self,view=None):
        """
        Renders the world.
        """
        super(StaticWorld,self).render3d(view)
        self.batch3d.draw()

class WorldView(object):
    """
    Object representing a view on the world.
    
    A :py:class:`WorldView()` object references a camera and has a name.
    
    ``cam`` is a valid camera name known to the world object supplied.
    """
    def __init__(self,world,name,cam):
        self.world = world
        self.name = name
        self.activeCamera = cam
        self.cam.on_activate(None)
    
    def setActiveCamera(self,name):
        """
        Sets the active camera.
        
        This method also calls the :py:meth:`Camera.on_activate() <peng3d.camera.Camera.on_activate>` event handler if the camera is not already active.
        """
        if name == self.activeCamera:
            return # Cam is already active
        if name not in self.world.cameras:
            raise ValueError("Unknown camera name")
        old = self.activeCamera
        self.activeCamera = name
        self.cam.on_activate(old)
    
    # Event handlers
    
    def on_menu_enter(self,old):
        """
        Fake event handler called by :py:meth:`Layer.on_menu_enter() <peng3d.layer.Layer.on_menu_enter>` when the containing menu is entered.
        """
        self.world.peng.window.push_handlers(self)
    def on_menu_exit(self,new):
        """
        Fake event handler, same as :py:meth:`on_menu_enter()` but for exiting menus instead.
        """
        self.world.peng.window.pop_handlers()
    
    # Proxy for self.cameras[self.activeCamera]
    @property
    def cam(self):
        """
        Property for getting the currently active camera.
        
        Always equals ``self.cameras[self.activeCamera]``\ .
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
        
        The value of this property will always be a list of length 3.
        
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
    """
    Subclass of :py:class:`WorldView()` that is rotatable using the user.
    
    Moving the mouse cursor left or right will rotate the attached camera horizontally and moving the mouse cursor up or down will rotate the camera vertically.
    
    By default, each pixel travelled changes the angle in degrees by 0.15, though this can be changed via the :confval:`controls.mouse.sensitivity` config value.
    """
    def on_menu_enter(self,old):
        """
        Fake event handler, same as :py:meth:`WorldView.on_menu_enter()` but forces mouse exclusivity.
        """
        super(WorldViewMouseRotatable,self).on_menu_enter(old)
        self.world.peng.window.toggle_exclusivity(True)
    def on_menu_exit(self,new):
        """
        Fake event handler, same as :py:meth:`WorldView.on_menu_exit()` but force-disables mouse exclusivity.
        """
        super(WorldViewMouseRotatable,self).on_menu_exit(new)
        self.world.peng.window.toggle_exclusivity(False)
    def on_key_press(self,symbol,modifiers):
        """
        Keyboard event handler handling only the escape key.
        
        If an escape key press is detected, mouse exclusivity is toggled via :py:meth:`PengWindow.toggle_exclusivity()`\ .
        """
        if symbol == key.ESCAPE:
            self.world.peng.window.toggle_exclusivity()
            return pyglet.event.EVENT_HANDLED
    def on_mouse_motion(self, x, y, dx, dy):
        """
        Handles mouse motion and rotates the attached camera accordingly.
        
        For more information about how to customize mouse movement, see the class documentation here :py:class:`WorldViewMouseRotatable()`\ .
        """
        if not self.world.peng.window.exclusive:
            return
        m = self.world.peng.cfg["controls.mouse.sensitivity"]
        x, y = self.rot
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        x %= 360
        newrot = (x,y)
        self.rot= newrot
    def on_mouse_drag(self,x,y,dx,dy,buttons,modifiers):
        """
        Handler used to still enable mouse movement while a button is pressed.
        """
        self.on_mouse_motion(x,y,dx,dy)
