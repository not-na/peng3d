#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui_menus.py
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

langs = ["en", "de", "__"]


def createGUI():
    # Adds a Resource Category for later use
    # Required to store Images for use in ImageButton, ImageWidgetLayer etc.
    # This creates a pyglet TextureBin internally, to bundle multiple images into one texture
    peng.resourceMgr.addCategory("gui")

    # Create GUI SubMenu and register it immediately
    s_start = peng3d.gui.SubMenu("start", m_main)

    # Insert Widget Initialization Code here

    ##### Basic Dialog
    sm_basic = peng3d.gui.DialogSubMenu(
        "test_dialog",
        m_main,
    )
    sm_basic.addAction("click_ok", print, tl("i18n:common.ok"))
    sm_basic.addAction("enter", print, tl("i18n:common.enter"))
    sm_basic.addAction("exit", print, tl("i18n:common.exit"))

    # Trigger Basic Dialog
    ss_btn_basic = peng3d.gui.Button(
        "btn_dialog",
        s_start,
        pos=lambda sw, sh, bw, bh: (
            sw / 2.0 - bw / 2.0,
            sh / 2.0 - bh / 2.0 + bh * 1.2,
        ),
        size=[-1, 50],
        min_size=[200, 50],
        label=tl("i18n:gui_menus.basic.label"),
        borderstyle="oldshadow",
    )
    ss_btn_basic.addAction("click", sm_basic.activate)

    ##### Confirm Dialog
    sm_confirm = peng3d.gui.ConfirmSubMenu(
        "test_confirm",
        m_main,
    )
    sm_confirm.setBackground([255, 100, 100])
    sm_confirm.addAction("confirm", print, tl("i18n:common.confirmed"))
    sm_confirm.addAction("cancel", print, tl("i18n:common.cancelled"))
    sm_confirm.addAction("enter", print, tl("i18n:common.enter"))
    sm_confirm.addAction("exit", print, tl("i18n:common.exit"))

    # Trigger Confirm Dialog
    ss_btn_confirm = peng3d.gui.Button(
        "btn_confirm",
        s_start,
        pos=lambda sw, sh, bw, bh: (sw / 2.0 - bw / 2.0, sh / 2.0 - bh / 2.0),
        size=[-1, 50],
        min_size=[200, 50],
        label=tl("i18n:gui_menus.confirm.label"),
        borderstyle="oldshadow",
    )
    ss_btn_confirm.addAction("click", sm_confirm.activate)

    ##### Text Dialog
    sm_text = peng3d.gui.TextSubMenu("test_text", m_main, peng.window, peng)
    sm_text.timeout = 5
    sm_text.addAction("enter", print, tl("i18n:common.enter"))
    sm_text.addAction("exit", print, tl("i18n:common.exit"))

    # Trigger Text Dialog
    ss_btn_text = peng3d.gui.Button(
        "btn_text",
        s_start,
        pos=lambda sw, sh, bw, bh: (
            sw / 2.0 - bw / 2.0,
            sh / 2.0 - bh / 2.0 - bh * 1.2,
        ),
        size=[-1, 50],
        min_size=[200, 50],
        label=tl("i18n:gui_menus.text.label"),
        borderstyle="oldshadow",
    )
    ss_btn_text.addAction("click", sm_text.activate)

    ##### Progress Dialog
    sm_progress = peng3d.gui.ProgressSubMenu(
        "test_progress",
        m_main,
        label_progressbar=tl("i18n:gui_menus.progress.plabel"),
    )
    sm_progress.addAction("enter", print, tl("i18n:common.enter"))
    sm_progress.addAction("exit", print, tl("i18n:common.exit"))
    sm_progress.addAction("enter", setattr, sm_progress, "progress_n", 0)
    sm_progress.auto_exit = True

    # Trigger Progress Dialog
    ss_btn_progress = peng3d.gui.Button(
        "btn_progress",
        s_start,
        pos=lambda sw, sh, bw, bh: (
            sw / 2.0 - bw / 2.0,
            sh / 2.0 - bh / 2.0 - bh * 2.4,
        ),
        size=[-1, 50],
        min_size=[200, 50],
        label=tl("i18n:gui_menus.progress.label"),
        borderstyle="oldshadow",
    )
    ss_btn_progress.addAction("click", sm_progress.activate)

    def f(*args):
        if m_main.activeSubMenu == "test_progress":
            sm_progress.progress_n = sm_progress.progress_n + 0.2

    pyglet.clock.schedule_interval(f, 1 / 60.0)

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
    m_main = peng3d.GUIMenu("main", peng.window, borderstyle="oldshadow")
    peng.window.addMenu(m_main)
    m_main.setBackground([200, 255, 100])

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
