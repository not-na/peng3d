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

__all__ = ["Layer", "Layer2D", "Layer3D"]

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
    When using the :py:meth:`draw()` method of this class, you will only need to use world coordinates, not camera coordinates.
    This allows for easy building of Games using First-Person-Perspectives.
    """
    def predraw(self):
        self.window.set3d()
