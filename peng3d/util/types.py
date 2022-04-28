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
    "DynPosition",
    "DynSize",
]

from typing import List, NewType, Union, Callable, Tuple

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

BorderStyle = str  # NewType("BorderStyle", str)
"""
Border style identifier.

Currently an alias of ``str``\\ , but may be changed to either an enum or custom type at
a later time.
"""

BackgroundType = Union["Layer", Callable, list, tuple, "Background", str]
"""
Type encompassing all allowed types for backgrounds of menus and submenus.

.. seealso::
    See :py:meth:`~peng3d.gui.SubMenu.setBackground()` for further details.
"""

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
