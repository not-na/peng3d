#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_layered.py
#  
#  Copyright 2017 notna <notna@apparat.org>
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

# Standard Pyglet imports
# Found near the top of most OpenGL-using files in peng3d
import pyglet
from pyglet.gl import *

# Imports peng3d (obvious)
import peng3d

def createGUI():
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")
    
    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu("start",m_main,peng.window,peng)
    m_main.addSubMenu(s_start)
    
    s_start.setBackground([242,241,240])
    
    # Simple Layered Button
    btn_ex1 = peng3d.gui.LayeredWidget("btn_ex1",s_start,peng.window,peng,
                                # at the center
                                pos=lambda sw,sh,bw,bh: (sw/2.-bw/2.,sh/2.-bh/2.),
                                size=[100,100],
                                )
    s_start.addWidget(btn_ex1)
    
    # Dynamic Button-like layer using images for different states
    #btn_ex1.addLayer(peng3d.gui.ImageButtonWidgetLayer("imgbtn",btn_ex1,
    #                        img_idle=["test_gui:gui.testbtn","gui"],
    #                        img_pressed=["test_gui:gui.testbtn-pressed","gui"],
    #                        img_hover=["test_gui:gui.testbtn-hover","gui"],
    #                        img_disabled=["test_gui:gui.testbtn-disabled","gui"]
    #                        )
    #                )
    # Dynamic Button-like layer using dynamically generated borders for different states
    btn_ex1.addLayer(peng3d.gui.ButtonBorderWidgetLayer("border",btn_ex1,
                            style="oldshadow",
                            )
                    )
    # Static Image Layer with additional border to show underlying layers
    btn_ex1.addLayer(peng3d.gui.ImageWidgetLayer("img",btn_ex1,
                            # Uses the resources of test_gui.py
                            img=["test_gui:gui.testbtn","gui"],
                            border=[4,4],
                            )
                    )
    # Plaintext label automatically centered on the parent widget
    #btn_ex1.addLayer(peng3d.gui.LabelWidgetLayer("label",btn_ex1,
    #                        label="Lorem"
    #                        )
    #                )
    # HTML Label automatically centered on the parent widget
    # Note that only some HTML Tags are supported
    btn_ex1.addLayer(peng3d.gui.HTMLLabelWidgetLayer("htmllabel",btn_ex1,
                            label="E=mc<sup>2</sup>", # I know that it is not complete, just for show
                            font_size=16,
                            #font_color=[62,67,73,255], # Pyglet docs text color
                            font_color=[255,255,255,255],
                            )
                    )
    
    # Set SubMenu as selected at the end, to avoid premature rendering with widgets missing
    # Should not happen normally, but still a good practice
    m_main.changeSubMenu("start")

def main(args):
    # Define these as global variables for easier access
    global peng, m_main
    
    # Create Peng instance
    peng = peng3d.Peng()
    # Create Window with caption
    peng.createWindow(caption="Peng3d Example",resizable=True,vsync=True)
    # Create main GUI Menu and register it immediately
    m_main = peng3d.GUIMenu("main",peng.window,peng)
    peng.window.addMenu(m_main)
    
    # Actually creates the GUI
    # In a separate function for clarity and readability
    createGUI()
    
    # Switch to the main menu and start the main loop
    peng.window.changeMenu("main")
    peng.run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
