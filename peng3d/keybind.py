#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  keybind.py
#
#  Copyright 2016-2022 notna <notna@apparat.org>
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

from typing import TYPE_CHECKING, Dict, Callable, List, Any

if TYPE_CHECKING:
    import peng3d


MOD_RELEASE = 1 << 15  # Additional fake modifier applied if on_key_release is called
"""
Fake modifier applied when a key is released instead of pressed.

This modifier internally has the value of ``1<<15`` and should thus be safe from any added modifiers in the future.

Note that this modifier is only applied within keybinds, not in regular ``on_key_down`` and ``on_key_up`` handlers.
"""

MODNAME2MODIFIER = bidict.OrderedBidict(
    [
        (
            "ctrl",
            key.MOD_ACCEL,
        ),  # For compat between MacOSX and everything else, equals to MOD_COMMAND on OSX and MOD_CTRL everywhere else
        ("alt", key.MOD_ALT),
        ("shift", key.MOD_SHIFT),
        # ("control",key.MOD_ACCEL),
        # Currently disabled due to bidict not allowing duplicate values
        ("option", key.MOD_OPTION),  # MacOSX only
        ("capslock", key.MOD_CAPSLOCK),
        ("numlock", key.MOD_NUMLOCK),
        ("scrolllock", key.MOD_SCROLLLOCK),
        # ("release",MOD_RELEASE), # Deprecated, use the released flag instead
    ]
)
"""
Ordered Bidict that maps between user-friendly names and internal constants.

Note that since this is a bidict, you can query the reverse mapping by accessing :py:attr:`MODNAME2MODIFIER.inv`\\ .
The non-inverse mapping maps from user-friendly name to internal constant.

This mapping is used by the Keybind system to convert the modifier constants to names.

The Mapping is as follows:

================ =============================== =======
Name             Pyglet constant                 Notes
================ =============================== =======
ctrl             :py:data:`key.MOD_ACCEL`
alt              :py:data:`key.MOD_ALT`          1
shift            :py:data:`key.MOD_SHIFT`
option           :py:data:`key.MOD_OPTION`
capslock         :py:data:`key.MOD_CAPSLOCK`
numlock          :py:data:`key.MOD_NUMLOCK`
scrollock        :py:data:`key.MOD_SCROLLOCK`
================ =============================== =======

1: automatically replaced by MOD_CTRL on Darwin/OSX
"""
if pyglet.compat_platform == "darwin":
    MODNAME2MODIFIER["alt"] = key.MOD_CTRL

OPTIONAL_MODNAMES = ["capslock", "numlock", "scrollock"]
"""
List of modifiers that are not substantial to a key combo.

If the :confval:`controls.keybinds.strict` option is disabled, every key combo is emitted with and without the modifiers in this list.
Else, only the combo with these modifiers is emitted.

This may cause no more combos to get through if numlock or capslock are activated.
"""


KeybindHandlerFunc = Callable[[int, int, bool], Any]
"""
Custom type for a keybind handler function.

See :py:meth:`KeybindHandler.add()` for more details regarding the signature.
"""


class KeybindHandler(object):
    """
    Handler class that automatically converts incoming key events to key combo events.

    A keybinding always is of format ``[MOD1-[MOD2-]]KEY`` with potentially more modifiers.

    See :py:data:`MODNAME2MODIFIER` for more information about existing modifiers.

    Note that the order in which modifiers are listed also is the order of the above listing.

    Keybindings are matched exactly, and optionally a second time without the modifiers listed in :py:data:`OPTIONAL_MODNAMES` if :confval:`controls.keybinds.strict` is set to False.
    """

    def __init__(self, peng: "peng3d.Peng"):
        self.peng: "peng3d.Peng" = peng
        self.peng.registerEventHandler("on_key_press", self.on_key_press)
        self.peng.registerEventHandler("on_key_release", self.on_key_release)
        self.keybinds: Dict[str, List[str]] = {}
        self.keybinds_nm: Dict[str, List[str]] = {}
        self.kbname: bidict.bidict[str, KeybindHandlerFunc] = bidict.bidict()

    def add(
        self, keybind: str, kbname: str, handler: KeybindHandlerFunc, mod: bool = True
    ) -> None:
        """
        Adds a keybind to the internal registry.

        Keybind names should be of the format ``namespace:category.subcategory.name``\\ e.g. ``peng3d:actor.player.controls.forward`` for the forward key combo for the player actor.

        :param str keybind: Keybind string, as described above
        :param str kbname: Name of the keybind, may be used to later change the keybinding without re-registering
        :param function handler: Function or any other callable called with the positional arguments ``(symbol,modifiers,release)`` if the keybind is pressed or released
        :param int mod: If the keybind should respect modifiers
        """
        keybind = keybind.lower()
        if mod:
            if keybind not in self.keybinds:
                self.keybinds[keybind] = []
            self.keybinds[keybind].append(kbname)
        else:
            if keybind not in self.keybinds_nm:
                self.keybinds_nm[keybind] = []
            self.keybinds_nm[keybind].append(kbname)
        self.kbname[kbname] = handler
        self.peng.sendEvent(
            "peng3d:keybind.add",
            {
                "peng": self.peng,
                "keybind": keybind,
                "kbname": kbname,
                "handler": handler,
                "mod": mod,
            },
        )

    def changeKeybind(self, kbname: str, combo: str) -> None:
        """
        Changes a keybind of a specific keybindname.

        :param str kbname: Same as kbname of :py:meth:`add()`
        :param str combo: New key combination
        """
        for key, value in self.keybinds.items():
            if kbname in value:
                del value[value.index(kbname)]
                break
        if combo not in self.keybinds:
            self.keybinds[combo] = []
        self.keybinds[combo].append(kbname)
        self.peng.sendEvent(
            "peng3d.keybind.change",
            {"peng": self.peng, "kbname": kbname, "combo": combo},
        )

    def mod_is_held(self, modname: str, modifiers: int) -> bool:
        """
        Helper method to simplify checking if a modifier is held.

        :param str modname: Name of the modifier, see :py:data:`MODNAME2MODIFIER`
        :param int modifiers: Bitmask to check in, same as the modifiers argument of the on_key_press etc. handlers
        """
        modifier = MODNAME2MODIFIER[modname.lower()]
        return modifiers & modifier

    def on_key_press(self, symbol, modifiers, release=False):
        # Format: "MOD1-MOD2-MOD3-KEY" in all lowercase
        modnames = []
        for modname in MODNAME2MODIFIER:
            if self.mod_is_held(modname, modifiers):
                modnames.append(modname)
        keyname = key.symbol_string(symbol)
        modnames.append(keyname)
        combo = "-".join(modnames).lower()
        self.handle_combo(combo, symbol, modifiers, release, True)
        self.handle_combo(keyname.lower(), symbol, modifiers, release, False)
        if not self.peng.cfg["controls.keybinds.strict"]:
            newmodnames = []
            for modname in modnames:
                if modname not in OPTIONAL_MODNAMES:
                    newmodnames.append(modname)
            if newmodnames == modnames:
                return
            combo = "-".join(newmodnames).lower()
            self.handle_combo(combo, symbol, modifiers, release, True)

    def handle_combo(
        self,
        combo: str,
        symbol: int,
        modifiers: int,
        release: bool = False,
        mod: bool = True,
    ) -> None:
        """
        Handles a key combination and dispatches associated events.

        First, all keybind handlers registered via :py:meth:`add` will be handled,
        then the pyglet event :peng3d:pgevent:`on_key_combo` with params ``(combo,symbol,modifiers,release,mod)`` is sent to the :py:class:`Peng()` instance.

        Also sends the events :peng3d:event:`peng3d:keybind.combo`\\, :peng3d:event:`peng3d:keybind.combo.press` and :peng3d:event`peng3d:keybind.combo.release`\\ .

        :params str combo: Key combination pressed
        :params int symbol: Key pressed, passed from the same argument within pyglet
        :params int modifiers: Modifiers held while the key was pressed
        :params bool release: If the combo was released
        :params bool mod: If the combo was sent without mods
        """
        if self.peng.cfg["controls.keybinds.debug"]:
            print("combo: nm=%s %s" % (mod, combo))
        if mod:
            for kbname in self.keybinds.get(combo, []):
                self.kbname[kbname](symbol, modifiers, release)
        else:
            for kbname in self.keybinds_nm.get(combo, []):
                self.kbname[kbname](symbol, modifiers, release)
        self.peng.sendPygletEvent(
            "on_key_combo", (combo, symbol, modifiers, release, mod)
        )
        self.peng.sendEvent(
            "peng3d:keybind.combo",
            {
                "peng": self.peng,
                "combo": combo,
                "symbol": symbol,
                "modifiers": modifiers,
                "release": release,
                "mod": mod,
            },
        )
        if release:
            self.peng.sendEvent(
                "peng3d:keybind.combo.release",
                {
                    "peng": self.peng,
                    "combo": combo,
                    "symbol": symbol,
                    "modifiers": modifiers,
                    "release": release,
                    "mod": mod,
                },
            )
        else:
            self.peng.sendEvent(
                "peng3d:keybind.combo.press",
                {
                    "peng": self.peng,
                    "combo": combo,
                    "symbol": symbol,
                    "modifiers": modifiers,
                    "release": release,
                    "mod": mod,
                },
            )

    def on_key_release(self, symbol, modifiers):
        # self.on_key_press(symbol,modifiers|MOD_RELEASE)
        self.on_key_press(symbol, modifiers, release=True)
