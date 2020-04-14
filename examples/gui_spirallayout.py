#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui_spirallayout.py
#  
#  Copyright 2020 notna <notna@apparat.org>
#  
#  This file is part of peng3d.
#
#  peng3d is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  peng3d is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with peng3d.  If not, see <http://www.gnu.org/licenses/>.
#

# Standard Pyglet imports
# Found near the top of most OpenGL-using files in peng3d
import pyglet
from pyglet.gl import *

# Imports peng3d (obvious)
import peng3d

langs = ["en", "de", "__"]


MAX_LEVELS = 8
# WARNING: a high max level may cause performance issues

# Thanks to @gunthobald for help with the formula for swapping buttons and sub-levels

def add_horizontal(submenu, parent, level):
    # Parent is vertical, we are horizontal
    x = level % 4
    l = peng3d.gui.layout.GridLayout(peng, parent, [2, 1], [0, 0])
    btn = peng3d.gui.Button(f"btn_l{level}", submenu, peng.window, peng,
                             pos=l.get_cell([x<2, 0], [1, 1]),
                             label=f"L{level}H",
                             )
    submenu.addWidget(btn)

    if level+1 < MAX_LEVELS:
        add_vertical(submenu, l.get_cell([x>=2, 0], [1, 1]), level+1)


def add_vertical(submenu, parent, level):
    # Parent is horizontal, we are vertical
    x = level % 4
    l = peng3d.gui.layout.GridLayout(peng, parent, [1, 2], [0, 0])
    btn = peng3d.gui.Button(f"btn_l{level}", submenu, peng.window, peng,
                            pos=l.get_cell([0, x<2], [1, 1]),
                            label=f"L{level}V",
                            )
    submenu.addWidget(btn)

    if level+1 < MAX_LEVELS:
        add_horizontal(submenu, l.get_cell([0, x>=2], [1, 1]), level+1)


def createGUI():
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")

    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu("start", m_main, peng.window, peng,
                                 borderstyle="oldshadow",
                                 )
    m_main.addSubMenu(s_start)

    s_start.setBackground([242, 241, 240])

    add_horizontal(s_start, s_start, 0)

    # Set SubMenu as selected at the end, to avoid premature rendering with widgets missing
    # Should not happen normally, but still a good practice
    m_main.changeSubMenu("start")


def main(args):
    # Define these as global variables for easier access
    global peng, m_main

    # Create Peng instance
    peng = peng3d.Peng()

    global t, tl
    t, tl = peng.t, peng.tl

    # Create Window with caption
    peng.createWindow(caption="Peng3d Example", resizable=True, vsync=True)
    # Create main GUI Menu and register it immediately
    m_main = peng3d.GUIMenu("main", peng.window, peng)
    peng.window.addMenu(m_main)

    def test_handler(symbol, modifiers, release):
        if release:
            return
        peng.i18n.setLang(langs[(langs.index(peng.i18n.lang) + 1) % len(langs)])

    peng.keybinds.add("f3", "testpy:handler.test", test_handler)

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
