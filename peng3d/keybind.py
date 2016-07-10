#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  keybind.py
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

import pyglet
from pyglet.window import key

import bidict

MOD_RELEASE = 1 << 15 # Additional fake modifier applied if on_key_released is called

MODNAME2MODIFIER = bidict.orderedbidict([
    ("ctrl",key.MOD_ACCEL), # For compat between MacOSX and everything else, equals to MOD_COMMAND on OSX and MOD_CTRL everywhere else
    ("alt",key.MOD_ALT),
    ("shift",key.MOD_SHIFT),
    #("control",key.MOD_ACCEL),
    # Currently disabled due to bidict not allowing duplicate values
    ("option",key.MOD_OPTION), # MacOSX only
    ("capslock",key.MOD_CAPSLOCK),
    ("numlock",key.MOD_NUMLOCK),
    ("scrolllock",key.MOD_SCROLLLOCK),
    ("release",MOD_RELEASE),
    ])
if pyglet.compat_platform=="darwin":
    MODNAME2MODIFIER["alt"]=key.MOD_CTRL

OPTIONAL_MODNAMES = ["capslock","numlock","scrollock"]

class KeybindHandler(object):
    def __init__(self,peng):
        self.peng = peng
        self.peng.registerEventHandler("on_key_press",self.on_key_press)
        self.peng.registerEventHandler("on_key_release",self.on_key_release)
        self.keybinds = {}
        self.kbname = bidict.bidict()
    def add(self,keybind,kbname,handler):
        keybind = keybind.lower()
        if keybind not in self.keybinds:
            self.keybinds[keybind]=[]
        self.keybinds[keybind].append(kbname)
        self.kbname[kbname]=handler
    def changeKeybind(self,kbname,handler):
        assert kbname in self.kbname
        self.kbname[kbname]=handler
    def mod_is_held(self,modname,modifiers):
        modifier = MODNAME2MODIFIER[modname.lower()]
        return modifiers&modifier
    def on_key_press(self,symbol,modifiers):
        # Format: "MOD1-MOD2-MOD3-KEY"
        modnames = []
        for modname in MODNAME2MODIFIER:
            if self.mod_is_held(modname,modifiers):
                modnames.append(modname)
        keyname = key.symbol_string(symbol)
        modnames.append(keyname)
        combo = "-".join(modnames).lower()
        self.handle_combo(combo,symbol,modifiers)
        if not self.peng.cfg["controls.keybinds.strict"]:
            newmodnames = []
            for modname in modnames:
                if modname not in OPTIONAL_MODNAMES:
                    newmodnames.append(modname)
            combo = "-".join(newmodnames).lower()
            self.handle_combo(combo,symbol,modifiers)
    def handle_combo(self,combo,symbol,modifiers):
        if self.peng.cfg["controls.keybinds.debug"]:
            print("combo: %s"%combo)
        for kbname in self.keybinds.get(combo,[]):
            self.kbname[kbname](symbol,modifiers)
        self.peng.handleEvent("on_key_combo",(combo,symbol,modifiers))
    def on_key_release(self,symbol,modifiers):
        self.on_key_press(symbol,modifiers|MOD_RELEASE)
