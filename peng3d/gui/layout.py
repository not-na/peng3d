#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  layout.py
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

__all__ = [
    "Layout", "GridLayout",
    "LayoutCell",
]

import peng3d
from peng3d import util

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Headless mode


class Layout(util.ActionDispatcher):
    """
    Base Layout class.

    This class does not serve any purpose directly other than to be a common base class
    for all layouts.

    Note that layouts can be nested, e.g. usually the first layouts parent is a SubMenu
    and sub-layouts get a LayoutCell of their parent layout as their parent.
    """
    def __init__(self, peng, parent):
        self.peng = peng
        self.parent = parent

    @property
    def pos(self):
        return self.parent.pos

    @property
    def size(self):
        return self.parent.size


class GridLayout(Layout):
    """
    Grid-based layout helper class.

    This class provides a grid-like layout to its sub-widgets. A border between widgets
    can be defined. Additionally, all widgets using this layout should automatically scale
    with screen size.
    """
    def __init__(self, peng, parent, res, border):
        super().__init__(peng, parent)

        self.res = res
        self.bordersize = border

    @property
    def cell_size(self):
        """
        Helper property defining the current size of cells in both x and y axis.

        :return: 2-tuple of float
        """
        return self.size[0]/self.res[0], self.size[1]/self.res[1]

    def get_cell(self, pos, size, anchor_x="left", anchor_y="bottom"):
        """
        Returns a grid cell suitable for use as the ``pos`` parameter of any widget.

        The ``size`` parameter of the widget will automatically be overwritten.

        :param pos: Grid position, in cell
        :param size: Size, in cells
        :param anchor_x: either ``left``\\ , ``center`` or ``right``
        :param anchor_y: either ``bottom``\\ , ``center`` or ``top``
        :return: LayoutCell subclass
        """
        return _GridCell(self.peng, self, pos, size, anchor_x, anchor_y)


class LayoutCell(object):
    @property
    def pos(self):
        raise NotImplementedError("pos property has to be overridden")

    @property
    def size(self):
        raise NotImplementedError("size property has to be overridden")


class _GridCell(LayoutCell):
    def __init__(self, peng, parent, offset, size, anchor_x, anchor_y):
        self.peng = peng
        self.parent = parent
        self.offset = offset
        self._size = size

        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

    @property
    def pos(self):
        dx, dy = self.parent.bordersize

        px, py = self.parent.pos            # Parent position in px
        oxc, oyc = self.offset              # Offset in cells
        csx, csy = self.parent.cell_size    # Cell size in px
        ox, oy = oxc*csx, oyc*csy           # Offset in px

        sxc, sxy = self._size               # Size in cells
        sx, sy = sxc*csx, sxy*csy           # Size in px

        if self.anchor_x == "left":
            x = px+ox+dx/2
        elif self.anchor_x == "center":
            x = px+ox+sx/2
        elif self.anchor_x == "right":
            x = px+ox+sx-dx/2
        else:
            raise ValueError(f"Invalid anchor_x of {self.anchor_x}")

        if self.anchor_y == "bottom":
            y = py+oy+dy/2
        elif self.anchor_y == "center":
            y = py+oy+sy/2
        elif self.anchor_y == "right":
            y = py+oy+sy-dy/2
        else:
            raise ValueError(f"Invalid anchor_y of {self.anchor_y}")

        return x, y

    @property
    def size(self):
        dx, dy = self.parent.bordersize
        csx, csy = self.parent.cell_size  # Cell size in px
        sxc, sxy = self._size  # Size in cells
        sx, sy = sxc * csx-dx, sxy * csy-dy

        return sx, sy
