#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui_responsive.py
#
#  Copyright 2022 notna <notna@apparat.org>
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


def createGUI():
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")

    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu("start", m_main, borderstyle="oldshadow")

    s_start.setBackground([242, 241, 240])

    r_l = peng3d.gui.ResponsiveLayout(peng, s_start)

    # Row 0
    button_a = peng3d.gui.Button(
        name="a",
        submenu=s_start,
        pos=r_l.row(height=100).col("a", xs=6, md=3, xxl=1),
        label="Button A",
    )

    button_b = peng3d.gui.Button(
        name="b",
        submenu=s_start,
        pos=r_l.row(0).col("b", xs=6, md=3, xxl=1),
        label="Button B",
    )

    button_c = peng3d.gui.Button(
        name="c",
        submenu=s_start,
        pos=r_l.row(0).col("c", xs=6, md=3, xxl=1),
        label="Button C",
    )

    # Row 1
    button_d = peng3d.gui.Button(
        name="d",
        submenu=s_start,
        pos=r_l.row(height=100).col("d", xs=6, md=3, xxl=1),
        label="Button D",
    )

    button_e = peng3d.gui.Button(
        name="e",
        submenu=s_start,
        pos=r_l.row(1).col("e", xs=2, sm=1),
        label="Button E",
    )

    # Row Outer
    button_f = peng3d.gui.Button(
        name="f",
        submenu=s_start,
        pos=r_l.row("outer", height=150).col("f", xs=12, hd=6, fhd=4, qhd=2, uhd=1),
        label="Button F",
    )

    button_g = peng3d.gui.Button(
        name="g",
        submenu=s_start,
        pos=r_l.row("outer").col("g", xs=12, hd=6, fhd=4, qhd=2, uhd=1),
        label="Button G",
    )

    button_h = peng3d.gui.Button(
        name="h",
        submenu=s_start,
        pos=r_l.row("outer").col("h", xs=12, hd=6, fhd=4, qhd=2, uhd=1),
        label="Button H",
    )

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
    peng.createWindow(
        caption_t="i18n:common.window.caption", resizable=True, vsync=True
    )
    # Create main GUI Menu and register it immediately
    m_main = peng3d.GUIMenu("main", peng.window)
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


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
