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

__all__ = ["Layer", "Layer2D", "Layer3D","LayerGroup","LayerWorld"]

try:
    import pyglet
except ImportError:
    pass

from . import camera

class Layer(object):
    """
    Base layer class.
    
    A Layer can be used to seperate background from foreground or the 3d world from a 2d HUD.
    
    This class by itself does nothing, you will need to subclass it and override the :py:meth:`draw()` method.
    """
    
    def __init__(self,menu,window,peng):
        self.window = window
        self.menu = menu
        self.peng = peng
        self.enabled = True
    
    # Subclass overrides
    def draw(self):
        """
        Called when this layer needs to be drawn.
        
        Override this method in subclasses to redefine behaviour.
        """
        pass
    def predraw(self):
        """
        Called before the :py:meth:`draw()` method is called.
        
        This method is used in the :py:class:`Layer2D()` and :py:class:`Layer3D()` subclasses for setting OpenGL state.
        
        Override this method in subclasses to redefine behaviour.
        """
        pass
    def postdraw(self):
        """
        Called after the :py:meth:`draw()` method is called.
        
        This method can be used to reset OpenGL state to avoid conflicts with other code.
        
        Override this method in subclasses to redefine behaviour.
        """
        pass
    # End subclass overrides
    
    # Event handlers
    
    def on_menu_enter(self,old):
        """
        Custom fake event handler called by :py:meth:`Menu.on_enter()` for every layer.
        
        Useful for adding and removing event handlers per layer.
        """
        pass
    def on_menu_exit(self,new):
        """
        Custom fake event handler called by :py:meth:`Menu.on_exit()` for every layer.
        
        Useful for adding and removing event handlers per layer.
        """
        pass
    
    def _draw(self):
        if not self.enabled:
            return
        self.predraw()
        try:
            self.draw()
        except Exception:
            raise
        finally:
            self.postdraw()

class Layer2D(Layer):
    """
    2D Variant of :py:class:`Layer()` and a subclass of the former.
    
    This class makes use of the :py:meth:`predraw()` method to configure OpenGL to draw 2-Dimensionally.
    This class uses :py:meth:`PengWindow.set2d()` to set the 2D mode.
    
    When overriding the :py:meth:`predraw()` method, make sure to call the superclass.
    """
    def predraw(self):
        self.window.set2d()

class Layer3D(Layer):
    """
    3D Variant of :py:class:`Layer()` and a subclass of the former.
    
    This class works the same as :py:class:`Layer2D()`\ , only for 3D drawing instead.
    This class uses :py:meth:`PengWindow.set3d()` to set the 3D mode.
    
    Also, the correct :py:func:`glTranslatef()` and :py:func:`glRotatef()` are applied to simplify drawing objects.
    When writing the :py:meth:`draw()` method of this class, you will only need to use world coordinates, not camera coordinates.
    This allows for easy building of Games using First-Person-Perspectives.
    """
    def __init__(self,menu,window,peng,cam):
        super(Layer3D,self).__init__(menu,window,peng)
        if not isinstance(cam,camera.Camera):
            raise TypeError("cam must be of type Camera!")
        self.cam = cam
    def predraw(self):
        self.window.set3d(self.cam)

class LayerGroup(Layer):
    """
    Layer variant wrapping the supplied pyglet group.
    
    ``group`` may only be an instance of :py:class:`pyglet.graphics.Group`\ , else a :py:exc:`TypeError` will be raised.
    
    Also note that both the :py:meth:`predraw() <Layer.predraw()>` and :py:meth:`postdraw() <Layer.postdraw()>` methods are overwritten by this class.
    
    .. seealso::
       
       For more information about pyglet groups, see `the pyglet docs <http://pyglet.readthedocs.io/en/latest/programming_guide/graphics.html#setting-the-opengl-state>`_\ .
    
    """
    
    def __init__(self,menu,window,peng,group):
        super(LayerGroup,self).__init__(menu,window,peng)
        if not isinstance(group,pyglet.graphics.Group):
            raise TypeError("group must be an instance of pyglet.graphics.Group")
        self.group = group
    def predraw(self):
        self.group.set_state()
    def postdraw(self):
        self.group.unset_state()

class LayerWorld(Layer3D):
    """
    Subclass of :py:class:`Layer3D()` implementing a 3D Layer showing a specific :py:class:`WorldView`\ .
    
    All arguments passed to the constructor should be self-explanatory.
    
    Note that you may not set any of the attributes directly, or crashes and bugs may appear indirectly within a certain timeframe.
    """
    def __init__(self,menu,window,peng,world,viewname):
        super(LayerWorld,self).__init__(menu,window,peng,world.getView(viewname).cam)
        self.world = world
        self.viewname = viewname
        self.view = self.world.getView(self.viewname)
    def setView(self,name):
        """
        Sets the view used to the specified ``name``\ .
        
        The name must be known to the world or else a :py:exc:`ValueError` is raised.
        """
        if name not in self.world.views:
            raise ValueError("Invalid viewname for world!")
        self.viewname = viewname
        self.view = self.world.getView(self.viewname)
    def predraw(self):
        """
        Sets up the attributes used by :py:class:`Layer3D()` and calls :py:meth:`Layer3D.predraw()`\ .
        """
        self.cam = self.view.cam
        super(LayerWorld,self).predraw()
    def draw(self):
        """
        Draws the view using the :py:meth:`World.render3d()` method.
        """
        self.world.render3d(self.view)
    def on_menu_enter(self,old):
        """
        Passes the event through to the WorldView to allow for custom behaviour.
        """
        return self.view.on_menu_enter(old)
    def on_menu_exit(self,new):
        """
        Same as :py:meth:`on_menu_enter()`\ .
        """
        return self.view.on_menu_exit(new)
