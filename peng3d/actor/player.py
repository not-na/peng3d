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

__all__ = ["BasicPlayer","FirstPersonPlayer"]

import math

import pyglet

from . import Actor,RotatableActor

class BasicPlayer(RotatableActor):
    def __init__(self,peng,world,uuid=None,pos=[0,0,0],rot=[0,0]):
        super(BasicPlayer,self).__init__(peng,world,uuid,pos,rot)
        self.uuid = uuid

class FirstPersonPlayer(BasicPlayer):
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
        """
        Handler used to still enable mouse movement while a button is pressed.
        """
        self.on_mouse_motion(x,y,dx,dy)
