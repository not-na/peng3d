#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  player.py
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

__all__ = ["BasicPlayer","FirstPersonPlayer","FourDirectionalMoveController","EgoMouseRotationalController","BasicFlightController"]

import math

try:
    import pyglet
except ImportError:
    pass

from . import Actor,RotatableActor,Controller

class FourDirectionalMoveController(Controller):
    """
    Controller allowing the user to control the actor with the keyboard.
    
    You can configure the used keybinds with the :confval:`controls.controls.forward` etc.
    The keybinds can also be changed with their keybindnames, e.g. ``peng3d:actor.player.controls.forward`` for forward.
    
    The movement speed may also be changed via the :py:attr:`movespeed` instance attribute, which defaults to :confval:`controls.controls.movespeed`\ .
    
    You may also access the currently held keys via :py:attr:`move`\ , which is a list with 2 items, forwards/backwards and left/right.
    """
    def __init__(self,*args,**kwargs):
        super(FourDirectionalMoveController,self).__init__(*args,**kwargs)
        self.move = [0,0]
        self.movespeed = self.peng.cfg["controls.controls.movespeed"]
    def registerEventHandlers(self):
        """
        Registers needed keybinds and schedules the :py:meth:`update` Method.
        
        You can control what keybinds are used via the :confval:`controls.controls.forward` etc. Configuration Values.
        """
        # Forward
        self.peng.keybinds.add(self.peng.cfg["controls.controls.forward"],"peng3d:actor.player.controls.forward",self.on_fwd_down,False)
        # Backward
        self.peng.keybinds.add(self.peng.cfg["controls.controls.backward"],"peng3d:actor.player.controls.backward",self.on_bwd_down,False)
        # Strafe Left
        self.peng.keybinds.add(self.peng.cfg["controls.controls.strafeleft"],"peng3d:actor.player.controls.strafeleft",self.on_left_down,False)
        # Strafe Right
        self.peng.keybinds.add(self.peng.cfg["controls.controls.straferight"],"peng3d:actor.player.controls.straferight",self.on_right_down,False)
        pyglet.clock.schedule_interval(self.update,1.0/60)
    def update(self,dt):
        """
        Should be called regularly to move the actor.
        
        This method does nothing if the :py:attr:`enabled` property is set to false.
        
        Note that this method is called automatically and should not be manually called.
        """
        if not self.enabled:
            return
        speed = self.movespeed
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        #dy+=self.vert*VERT_SPEED
        x,y,z = self.actor._pos
        newpos = dx+x, dy+y, dz+z
        self.actor.pos = newpos
    def get_motion_vector(self):
        """
        Returns the movement vector according to held buttons and the rotation.
        
        :return: 3-Tuple of ``(dx,dy,dz)``
        :rtype: tuple
        """
        if any(self.move):
            x, y = self.actor._rot
            strafe = math.degrees(math.atan2(*self.move))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            dy = 0.0
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    # Event Handlers
    def on_fwd_down(self,symbol,modifiers,release):
        self.move[0]-=1 if not release else -1
    def on_bwd_down(self,symbol,modifiers,release):
        self.move[0]+=1 if not release else -1
    
    def on_left_down(self,symbol,modifiers,release):
        self.move[1]-=1 if not release else -1
    def on_right_down(self,symbol,modifiers,release):
        self.move[1]+=1 if not release else -1

class EgoMouseRotationalController(Controller):
    """
    Controller allowing the user to rotate the actor with the mouse.
    """
    def __init__(self,*args,**kwargs):
        super(EgoMouseRotationalController,self).__init__(*args,**kwargs)
    def registerEventHandlers(self):
        """
        Registers the motion and drag handlers.
        
        Note that because of the way pyglet treats mouse dragging, there is also an handler registered to the on_mouse_drag event.
        """
        self.world.registerEventHandler("on_mouse_motion",self.on_mouse_motion)
        self.world.registerEventHandler("on_mouse_drag",self.on_mouse_drag)
    def on_mouse_motion(self, x, y, dx, dy):
        if self.enabled:
            m = self.peng.cfg["controls.mouse.sensitivity"]
            x, y = self.actor._rot
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            x %= 360
            newrot = (x,y)
            self.actor.rot = newrot
    def on_mouse_drag(self,x,y,dx,dy,buttons,modifiers):
        self.on_mouse_motion(x,y,dx,dy)

class BasicFlightController(Controller):
    """
    Controller allowing the user to move up and down with the jump and crouch controls.
    
    The used keybinds may be configured via :confval:`controls.controls.crouch` and :confval:`controls.controls.jump`\ .
    
    The vertical speed used when flying may be configured via :confval:`controls.controls.verticalspeed` or the :py:attr:`speed` attribute.
    """
    def __init__(self,*args,**kwargs):
        super(BasicFlightController,self).__init__(*args,**kwargs)
        self.speed = self.peng.cfg["controls.controls.verticalspeed"]
        self.move = 0
    def registerEventHandlers(self):
        """
        Registers the up and down handlers.
        
        Also registers a scheduled function every 60th of a second, causing pyglet to redraw your window with 60fps.
        """
        # Crouch/fly down
        self.peng.keybinds.add(self.peng.cfg["controls.controls.crouch"],"peng3d:actor.player.controls.crouch",self.on_crouch_down,False)
        # Jump/fly up
        self.peng.keybinds.add(self.peng.cfg["controls.controls.jump"],"peng3d:actor.player.controls.jump",self.on_jump_down,False)
        pyglet.clock.schedule_interval(self.update,1.0/60)
    def update(self,dt):
        """
        Should be called regularly to move the actor.
        
        This method does nothing if the :py:attr:`enabled` property is set to False.
        
        This method is called automatically and should not be called manually.
        """
        if not self.enabled:
            return
        dy = self.speed * dt * self.move
        x,y,z = self.actor._pos
        newpos = x,dy+y,z
        self.actor.pos = newpos
    
    def on_crouch_down(self,symbol,modifiers,release):
        self.move -= 1 if not release else -1
    def on_jump_down(self,symbol,modifiers,release):
        self.move += 1 if not release else -1

class BasicPlayer(RotatableActor):
    """
    Basic Player class, subclass of :py:class:`RotatableActor()`\ .
    
    This class adds no features currently, it can be used to identify player actors via :py:func:`isinstance()`\ .
    """
    pass

class FirstPersonPlayer(BasicPlayer):
    """
    Old class allowing to create standard first-person players easily.
    
    :deprecated: See :py:class:`EgoMouseRotationalController()` and :py:class:`FourDirectionalMoveController()` instead
    """
    def __init__(self,peng,world,uuid=None,pos=[0,0,0],rot=[0,0]):
        super(FirstPersonPlayer,self).__init__(peng,world,uuid,pos,rot)
        self.move = [0,0]
        self.movespeed = self.peng.cfg["controls.controls.movespeed"]
        self.active = True
        
        # Event handler registration
        # Forward
        self.peng.keybinds.add(self.peng.cfg["controls.controls.forward"],"peng3d:actor.player.controls.forward",self.on_fwd_down)
        self.peng.keybinds.add("release-"+self.peng.cfg["controls.controls.forward"],"peng3d:actor.player.controls.forward.release",self.on_fwd_up)
        # Backward
        self.peng.keybinds.add(self.peng.cfg["controls.controls.backward"],"peng3d:actor.player.controls.backward",self.on_bwd_down)
        self.peng.keybinds.add("release-"+self.peng.cfg["controls.controls.backward"],"peng3d:actor.player.controls.backward.release",self.on_bwd_up)
        # Strafe Left
        self.peng.keybinds.add(self.peng.cfg["controls.controls.strafeleft"],"peng3d:actor.player.controls.strafeleft",self.on_left_down)
        self.peng.keybinds.add("release-"+self.peng.cfg["controls.controls.strafeleft"],"peng3d:actor.player.controls.strafeleft.release",self.on_left_up)
        # Strafe Right
        self.peng.keybinds.add(self.peng.cfg["controls.controls.straferight"],"peng3d:actor.player.controls.straferight",self.on_right_down)
        self.peng.keybinds.add("release-"+self.peng.cfg["controls.controls.straferight"],"peng3d:actor.player.controls.straferight.release",self.on_right_up)
        # Mouse
        self.world.registerEventHandler("on_mouse_motion",self.on_mouse_motion)
        self.world.registerEventHandler("on_mouse_drag",self.on_mouse_drag)
        pyglet.clock.schedule_interval(self.update,1.0/60)
    def update(self,dt):
        """
        Internal method used for moving the player.
        
        :param float dt: Time delta since the last call to this method
        """
        speed = self.movespeed
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        #dy+=self.vert*VERT_SPEED
        x,y,z = self._pos
        newpos = dx+x, dy+y, dz+z
        self.pos = newpos
    def get_motion_vector(self):
        """
        Returns the movement vector according to held buttons and the rotation.
        
        :return: 3-Tuple of ``(dx,dy,dz)``
        :rtype: tuple
        """
        if any(self.move):
            x, y = self._rot
            strafe = math.degrees(math.atan2(*self.move))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            dy = 0.0
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    # Event Handlers
    def on_fwd_down(self,symbol,modifiers):
        self.move[0]-=1
    def on_fwd_up(self,symbol,modifiers):
        self.move[0]+=1
    
    def on_bwd_down(self,symbol,modifiers):
        self.move[0]+=1
    def on_bwd_up(self,symbol,modifiers):
        self.move[0]-=1
    
    def on_left_down(self,symbol,modifiers):
        self.move[1]-=1
    def on_left_up(self,symbol,modifiers):
        self.move[1]+=1
    
    def on_right_down(self,symbol,modifiers):
        self.move[1]+=1
    def on_right_up(self,symbol,modifiers):
        self.move[1]-=1
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.active:
            m = 0.15
            x, y = self._rot
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            x %= 360
            newrot = (x,y)
            self.rot = newrot
    def on_mouse_drag(self,x,y,dx,dy,buttons,modifiers):
        self.on_mouse_motion(x,y,dx,dy)
