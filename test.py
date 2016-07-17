#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test.py
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

import code
import threading

from pyglet.window import key

import peng3d

CONSOLE = False

TERRAIN = [-1,-1,-1, 1,-1,-1, 1,-1,1, -1,-1,1]

COLORS  = [255,0,0, 0,255,0, 0,0,255, 255,255,255]

def main(args):
    peng = peng3d.Peng()
    peng.createWindow(caption="Peng3d Test Project",resizable=True,vsync=True)
    peng.window.addMenu(peng3d.Menu("main",peng.window,peng))
    peng.window.toggle_exclusivity()
    def esc_toggle(symbol,modifiers):
        peng.window.toggle_exclusivity()
        player.controlleroptions["enabled"] = peng.window.exclusive
    peng.keybinds.add("escape","testpy:handler.esctoggle",esc_toggle)
    def test_handler(symbol,modifiers):
        peng.keybinds.changeKeybind("peng3d:actor.player.controls.forward","space")
        peng.keybinds.changeKeybind("peng3d:actor.player.controls.forward.release","release-space")
    peng.keybinds.add("f3","testpy:handler.test",test_handler)
    # Creates world/cam/view/player
    world = peng3d.StaticWorld(peng,TERRAIN,COLORS)
    #player = peng3d.actor.player.FirstPersonPlayer(peng,world)
    player = peng3d.actor.player.BasicPlayer(peng,world)
    player.addController(peng3d.actor.player.FourDirectionalMoveController(player))
    player.addController(peng3d.actor.player.EgoMouseRotationalController(player))
    world.addActor(player)
    c = peng3d.CameraActorFollower(world,"cam1",player)
    world.addCamera(c)
    v = peng3d.WorldView(world,"view1","cam1")
    world.addView(v)
    # Creates menu/layer
    m = peng3d.Menu("main",peng.window,peng)
    m.addWorld(world)
    peng.window.addMenu(m)
    l = peng3d.LayerWorld(m,peng.window,peng,world,"view1")
    m.addLayer(l)
    peng.window.changeMenu("main")
    # Done!
    if CONSOLE:
        t = threading.Thread(target=code.interact,name="REPL Thread",kwargs={"local":locals()})
        t.daemon = True
        t.start()
    peng.run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
