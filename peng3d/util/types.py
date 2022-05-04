#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  types.py
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
"""
This module contains various helper types used throughout ``peng3d``\\ .

Most of these types are aliases, which ensure compatibility with existing applications
that for example pass in literal values (which wouldn't be of a custom type without casting).
"""

__all__ = [
    "ColorRGB",
    "ColorRGBA",
    "ColorRGBFloat",
    "ColorRGBAFloat",
    "BorderStyle",
    "BackgroundType",
    "StyleValue",
    "DynPosition",
    "DynSize",
    "DynTranslateable",
]

from typing import List, NewType, Union, Callable, Tuple, Type

ColorRGB = List[int]
"""
RGB Color represented as three integers from zero to 255.
"""
ColorRGBA = List[int]
"""
RGBA Color represented as four integers from zero to 255.
"""

ColorRGBFloat = List[float]
"""
RGB Color represented as three floats from zero to one.
"""
ColorRGBAFloat = List[float]
"""
RGBA Color represented as four floats from zero to one.
"""

BorderStyle = Union[Type["Borderstyle"], str]
"""
Border style identifier.

Either a subclass of :py:class:`~peng3d.gui.style.Borderstyle()` or a string identifier.
"""

BackgroundType = Union[
    "Layer", Callable, list, tuple, "Background", str, Type["DEFER_BG"]
]
"""
Type encompassing all allowed types for backgrounds of menus and submenus.

.. seealso::
    See :py:meth:`~peng3d.gui.SubMenu.setBackground()` for further details.
"""

StyleValue = Union[float, str, BorderStyle]

DynPosition = Union[
    List[float],
    Callable[[float, float, float, float], Tuple[float, float]],
    "layout.LayoutCell",
]
"""
Dynamic position of a widget or container.

Can be either a static position as a list, a callback function or a :py:class:`~peng3d.layout.LayoutCell`\\ .
"""

DynSize = Union[List[float], Callable[[float, float], Tuple[float, float]], None]
"""
Dynamic size of a widget or container.

Can be either a static size as a list or a callback function. May be ``None`` if the position
is a :py:class:`~peng3d.layout.LayoutCell`\\ .
"""

DynTranslateable = Union[str, "_LazyTranslator"]
"""
A string that may be either fixed, translated or even dynamically translated.

If a method or class accepts this type, it means that it supports dynamic translation
of this attribute, unless indicated otherwise in its documentation.
"""
