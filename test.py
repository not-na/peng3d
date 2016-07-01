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

import peng3d

CONSOLE = False

TERRAIN = [-1,-1,-1, 1,-1,-1, 1,-1,1, -1,-1,1]

COLORS  = [255,0,0, 0,255,0, 0,0,255, 255,255,255]

def main(args):
    p = peng3d.Peng()
    if CONSOLE:
        t = threading.Thread(target=code.interact,name="REPL Thread",kwargs={"local":locals()})
        t.daemon = True
        t.start()
    p.createWindow(caption="Peng3d Test Project")
    p.window.addMenu(peng3d.Menu("main",p.window,p))
    # Creates world/cam/view
    w = peng3d.StaticWorld(p,TERRAIN,COLORS)
    c = peng3d.Camera(w,"cam1",[0,0,0])
    w.addCamera(c)
    v = peng3d.WorldViewMouseRotatable(w,"view1","cam1")
    w.addView(v)
    # Creates menu/layer
    m = peng3d.Menu("main",p.window,p)
    p.window.addMenu(m)
    l = peng3d.LayerWorld(m,p.window,p,w,"view1")
    m.addLayer(l)
    p.window.changeMenu("main")
    # Done!
    p.run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
