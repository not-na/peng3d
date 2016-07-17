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

__all__ = ["Actor","RotatableActor","Controller"]

import uuid as uuidm

class Controller(object):
    """
    Base class for all controllers.
    
    Controllers define behaviour of Actors and can be used to control them via e.g. the keyboard or an AI.
    
    Every controller is bound to its actor and can be enabled and disabled individually.
    You may also deactivate all controllers of an Actor by setting the ``enabled`` key of :py:attr:`Actor.controlleroptions` to False.
    """
    def __init__(self,actor):
        self.world = actor.world
        self.peng = actor.world.peng
        self.actor = actor
        self._enabled = True
        self.registerEventHandlers()
    def registerEventHandlers(self):
        """
        Method to be overridden by subclasses for registering event handlers.
        
        Automatically called upon object creation.
        """
        pass
    
    @property
    def enabled(self):
        """
        Property allowing to get and set if this controller should be active.
        
        When getting this property, the result of ANDing the internal flag and the actor flag is returned.
        
        When setting, only the local internal flag is set, allowing other controllers to still work.
        
        :raises AssertionError: when the supplied value is not of type bool
        """
        return self._enabled and self.actor.controlleroptions["enabled"]
    @enabled.setter
    def enabled(self,value):
        assert isinstance(value,bool)
        self._enabled = value

class Actor(object):
    """
    Actor object, base class for all other Actors in the world.
    
    An actor represents an object in the world, for example the player, an animal, enemy or dropped item.
    
    Everything that is not part of the terrain should be an actor.
    
    The default actor does not do anything, you should look at the subclasses for more information.
    """
    def __init__(self,peng,world,uuid=None,pos=[0,0,0]):
        self.peng = peng
        self.world = world
        self.uuid = uuid if uuid is not None else uuidm.uuid4()
        self.controllers = []
        self.controlleroptions = {
            "enabled":True
            }
        
        self._pos = pos
    
    def addController(self,controller):
        """
        Adds a controller to the actor.
        
        A controller can control its actor and can act as a bridge between actor and user inputs.
        
        Controllers may be added anytime during the lifetime of an actor.
        """
        self.controllers.append(controller)
    
    # Event handlers
    def on_move(self,old):
        """
        Fake event handler called if the location of this actor changes.
        
        This handler is called after the location has changed.
        
        :param list old: The previous position
        """
        pass
    
    # Properties
    @property
    def pos(self):
        """
        Property allowing access to the position of this actor.
        
        This actor is read-write but calls :py:meth:`on_move()` if it is set.
        """
        return self._pos
    @pos.setter
    def pos(self,value):
        old = self._pos
        self._pos = value
        self.on_move(old)

class RotatableActor(Actor):
    """
    Actor that can also be rotated.
    
    This subclass adds a rotational value to the actor and a method to move the actor along the current rotation.
    """
    def __init__(self,peng,world,uuid=None,pos=[0,0,0],rot=[0,0]):
        super(RotatableActor,self).__init__(peng,world,uuid,pos)
        self._rot = rot
    def move(self,dist):
        """
        Moves the actor using standard trigonometry along the current rotational vector.
        
        :param float dist: Distance to move
        
        .. todo::
           
           Test this method, also with negative distances
        """
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
        """
        Fake event handler called if the rotation of this actor changes.
        
        This handler is called after the rotation has been made.
        
        :param tuple old: Old rotation before rotating
        """
        pass
    
    # Properties
    @property
    def rot(self):
        """
        Property for accessing the rotation of this actor.
        
        Rotation is a tuple of ``(x,y)`` where y is clamped to -90 and 90.
        x rolls over at 360, resulting in a seamless experience for players.
        
        This property may also be written to, this calls :py:meth:`on_rotate()`\ .
        """
        return self._rot
    @rot.setter
    def rot(self,value):
        old = self._rot
        x,y = value
        y = max(-90, min(90, y))
        x %= 360
        self._rot = x,y
        self.on_rotate(old)
