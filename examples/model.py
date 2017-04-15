#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_gui.py
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

import pyglet
from pyglet.window import key
from pyglet.gl import *

import peng3d

CONSOLE = False

TERRAIN = [-1,-1,-1, 1,-1,-1, 1,-1,1, -1,-1,1]

COLORS  = [255,0,0, 0,255,0, 0,0,255, 255,255,255]

def createTexBin():
    global texBin
    texBin = pyglet.image.atlas.TextureBin(2048,2048)

def createGUI(main,game):
    global title,playbtn,optionsbtn,testbtn,tex, options,backbtn
    global gamel
    peng.resourceMgr.addCategory("gui")
    
    # Titlescreen
    title = peng3d.gui.SubMenu("titlescreen",main,peng.window,peng)
    title.setBackground([242,241,240])
    
    # Playbtn
    playbtn = peng3d.gui.Button("playbtn",title,peng.window,peng,
                                pos=lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.),
                                size=[100,100],
                                borderstyle="oldshadow",
                                label="Play",
                                )
    # Changes both the menu and enables exclusivity
    playbtn.addAction("click",peng.window.changeMenu,"game")
    playbtn.addAction("click",peng.window.toggle_exclusivity)
    playbtn.addAction("click",lambda: player.controlleroptions.__setitem__("enabled",True))
    title.addWidget(playbtn)
    
    # Optionsbtn
    optionsbtn = peng3d.gui.Button("optionsbtn",title,peng.window,peng,
                                pos=lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.-120),
                                size=[100,100],
                                borderstyle="oldshadow",
                                label="Options",
                                )
    # Changes submenu
    optionsbtn.addAction("click",main.changeSubMenu,"options")
    title.addWidget(optionsbtn)
    
    
    main.addSubMenu(title)
    
    # Options screen
    options = peng3d.gui.SubMenu("options",main,peng.window,peng)
    options.setBackground([242,241,240])
    
    # Backbtn
    backbtn = peng3d.gui.Button("backbtn",options,peng.window,peng,
                                pos=lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.-120),
                                size=[100,100],
                                borderstyle="oldshadow",
                                label="Back",
                                )
    # Changes submenu
    backbtn.addAction("click",main.changeSubMenu,"titlescreen")
    options.addWidget(backbtn)
    
    main.addSubMenu(options)
    
    main.changeSubMenu("titlescreen")
    
    # In-Game HUD/Pause Menu
    
    gamel = peng3d.gui.GUILayer("game",game,peng.window,peng)
    
    pause = peng3d.gui.SubMenu("pause",gamel,peng.window,peng)
    pause.setBackground([242,241,240,120])
    
    # Continuebtn
    continuebtn = peng3d.gui.Button("continuebtn",pause,peng.window,peng,
                                pos=lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.),
                                size=[100,100],
                                borderstyle="oldshadow",
                                label="Continue",
                                )
    # Returns to the game
    continuebtn.addAction("click",esc_toggle,0,0,False)
    pause.addWidget(continuebtn)
    
    gamel.addSubMenu(pause)
    
    hud = peng3d.gui.SubMenu("hud",gamel,peng.window,peng)
    hud.setBackground("blank")
    
    gamel.addSubMenu(hud)
    
    gamel.changeSubMenu("hud")
    game.addLayer(gamel)

def loadModel():
    global model
    #model = peng3d.model.Model(peng,peng.resourceMgr,"peng3d:model.test")
    model = peng.resourceMgr.getModel("peng3d:model.test")

def createTestEntity():
    global testactor
    testactor = peng3d.actor.RotateableActor(peng,world,pos=[2,0,2])
    world.addActor(testactor)
    
    testactor.addController(peng3d.actor.player.FourDirectionalMoveController(testactor))
    testactor.addController(peng3d.actor.player.EgoMouseRotationalController(testactor))
    testactor.addController(peng3d.actor.player.BasicFlightController(testactor))
    
    testactor.controlleroptions["enabled"]=False
    
    testactor.setModel(model)

def main(args):
    global peng,esc_toggle,world,player
    # Peng engine instance creation and creating the window
    peng = peng3d.Peng()
    peng.createWindow(caption="Peng3d GUI Test Project",resizable=True,vsync=True)
    peng.window.addMenu(peng3d.Menu("main",peng.window,peng))
    createTexBin()
    loadModel()
    #peng.window.toggle_exclusivity()
    
    # Keybinds
    def esc_toggle(symbol,modifiers,release):
        if release:
            return
        peng.window.toggle_exclusivity()
        player.controlleroptions["enabled"] = peng.window.exclusive
        if not peng.window.exclusive:
            gamel.changeSubMenu("pause")
        else:
            gamel.changeSubMenu("hud")
    peng.keybinds.add("escape","testpy:handler.esctoggle",esc_toggle)
    def test_handler(symbol,modifiers,release):
        if release:
            return
        testactor.controlleroptions["enabled"]=not testactor.controlleroptions["enabled"]
        player.controlleroptions["enabled"] = not testactor.controlleroptions["enabled"]
    peng.keybinds.add("f3","testpy:handler.test",test_handler)
    
    # Fog and clear color config
    peng.cfg["graphics.clearColor"]=[0.5,0.69,1.0,1.0]
    peng.cfg["graphics.fogSettings"]["enable"]=True
    peng.cfg["graphics.fogSettings"]["start"]=32
    peng.cfg["graphics.fogSettings"]["end"]=48
    
    # Creates world/cam/view/player
    world = peng3d.StaticWorld(peng,TERRAIN,COLORS)
    #player = peng3d.actor.player.FirstPersonPlayer(peng,world)
    player = peng3d.actor.player.BasicPlayer(peng,world)
    
    # Player controllers
    player.addController(peng3d.actor.player.FourDirectionalMoveController(player))
    player.addController(peng3d.actor.player.EgoMouseRotationalController(player))
    player.addController(peng3d.actor.player.BasicFlightController(player))
    
    # Player view/camera
    world.addActor(player)
    c = peng3d.CameraActorFollower(world,"cam1",player)
    world.addCamera(c)
    v = peng3d.WorldView(world,"view1","cam1")
    world.addView(v)
    
    # Test actor
    createTestEntity()
    
    # Creates menu/layer
    mgame = peng3d.Menu("game",peng.window,peng)
    mgame.addWorld(world)
    peng.window.addMenu(mgame)
    l = peng3d.LayerWorld(mgame,peng.window,peng,world,"view1")
    mgame.addLayer(l)
    
    # Create Main Menu
    mmain = peng3d.GUIMenu("main",peng.window,peng)
    peng.window.addMenu(mmain)
    createGUI(mmain,mgame)
    
    # Switch to the main menu
    peng.window.changeMenu("main")
    
    # Done!
    if CONSOLE:
        # Starts a console in seperate Thread, allows interactive debugging and testing stuff easily
        t = threading.Thread(target=code.interact,name="REPL Thread",kwargs={"local":locals()})
        t.daemon = True
        t.start()
    
    # Starts the main loop
    peng.run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
