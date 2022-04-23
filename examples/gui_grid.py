#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  template.py
#
#  Copyright 2020 notna <notna@apparat.org>
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

langs = ["en", "de", "__"]


def createGUI():
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")

    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu(
        "start",
        m_main,
        peng.window,
        peng,
        borderstyle="oldshadow",
    )
    m_main.addSubMenu(s_start)

    s_start.setBackground([242, 241, 240])

    def f():
        print(f"Sent form with {pwdin.password=}")

    s_start.addAction("send_form", f)

    layout = peng3d.gui.layout.GridLayout(peng, s_start, [4, 6], [10, 10])

    btn0 = peng3d.gui.Button(
        "btn0",
        s_start,
        peng.window,
        peng,
        pos=layout.get_cell([1, 4], [2, 1]),
        label="Send",
    )
    s_start.addWidget(btn0)

    btn0.addAction("click", s_start.send_form)

    btn1 = peng3d.gui.Button(
        "btn1",
        s_start,
        peng.window,
        peng,
        pos=layout.get_cell([1, 3], [2, 1]),
        label="Button 1",
    )
    s_start.addWidget(btn1)

    btn2 = peng3d.gui.Button(
        "btn2",
        s_start,
        peng.window,
        peng,
        pos=layout.get_cell([1, 2], [2, 1]),
        label="Button 2",
    )
    s_start.addWidget(btn2)

    btn3 = peng3d.gui.FramedImageButton(
        "btn3",
        s_start,
        peng.window,
        peng,
        pos=layout.get_cell([1, 1], [1, 1]),
        label="Button 3",
        bg_idle=["test_gui:gui.testbtn", "gui"],
        bg_hover=["test_gui:gui.testbtn-hover", "gui"],
        frame=[
            (6, 87, 7),
            (7, 87, 6),
        ],
        scale=[2, 1],
        repeat_edge=True,
        repeat_center=True,
    )
    s_start.addWidget(btn3)

    # btn4 = peng3d.gui.Button("btn4", s_start, peng.window, peng,
    #                          pos=layout.get_cell([2, 1], [1, 1]),
    #                          label="Button 4",
    #                          )
    # s_start.addWidget(btn4)
    pwdin = peng3d.gui.PasswordInput(
        "pwdin",
        s_start,
        peng.window,
        peng,
        pos=layout.get_cell([2, 1], [1, 1]),
        default="Password Field",
    )
    s_start.addWidget(pwdin)

    def f():
        print(f"Password changed: {pwdin.password}")

    pwdin.addAction("pwd_change", f)

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


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
