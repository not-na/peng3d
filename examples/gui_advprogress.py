#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui_advprogress.py
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

# Categories
# fourth number is speed in units/frame
categories = {
    "1": [0, 0, 100, 1],
    "2": [0, 0, 1000, 1],
}

langs = ["en", "de", "__"]


def createGUI():
    global sma_bar
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")

    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu("start", m_main, peng.window, peng)
    m_main.addSubMenu(s_start)

    s_start.setBackground([242, 241, 240])

    # Advanced Progress Dialog
    sm_advprog = peng3d.gui.AdvancedProgressSubMenu(
        "sm_advprog",
        m_main,
        peng.window,
        peng,
        label_progressbar=tl("i18n:gui_adv.progress.label"),
    )
    sm_advprog.setBackground([242, 241, 240])
    sm_advprog.addAction("enter", print, tl("i18n:common.enter"))
    sm_advprog.addAction("exit", print, tl("i18n:common.exit"))

    m_main.addSubMenu(sm_advprog)

    sma_bar = sm_advprog.wprogressbar

    # Trigger advprog dialog
    ss_btn_advprog = peng3d.gui.Button(
        "btn_advprog",
        s_start,
        peng.window,
        peng,
        pos=lambda sw, sh, bw, bh: (
            sw / 2.0 - bw / 2.0,
            sh / 2.0 - bh / 2.0 + bh * 1.2,
        ),
        size=[200, 50],
        label=tl("i18n:gui_adv.trigger.label"),
        borderstyle="oldshadow",
    )
    ss_btn_advprog.addAction("click", sm_advprog.activate)

    s_start.addWidget(ss_btn_advprog)

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

    for cname, cdat in categories.items():
        sma_bar.addCategory(cname, cdat[0], cdat[1], cdat[2])

    def update(dt=None):
        for cname, cdat in categories.items():
            nmin, n, nmax = sma_bar[cname]
            n += cdat[3]
            if n >= nmax:
                print(tl("i18n:gui_adv.wraparound") % cname)
            n %= nmax
            sma_bar.updateCategory(cname, n=n)

    pyglet.clock.schedule_interval(update, 1.0 / 60)

    # Switch to the main menu and start the main loop
    peng.window.changeMenu("main")
    peng.run()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
