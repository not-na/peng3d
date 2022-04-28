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
ColorRGBA = List[int]

ColorRGBFloat = List[float]
ColorRGBAFloat = List[float]

BorderStyle = str  # NewType("BorderStyle", str)

BackgroundType = Union["Layer", Callable, list, tuple, "Background", str]

DynPosition = Union[
    List[float],
    Callable[[float, float, float, float], Tuple[float, float]],
    "layout.LayoutCell",
]

DynSize = Union[List[float], Callable[[float, float], Tuple[float, float]], None]
