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
from peng3d.util import WatchingList

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

    def get_cell(self, pos, size, anchor_x="left", anchor_y="bottom", border=1):
        """
        Returns a grid cell suitable for use as the ``pos`` parameter of any widget.

        The ``size`` parameter of the widget will automatically be overwritten.

        :param pos: Grid position, in cell
        :param size: Size, in cells
        :param anchor_x: either ``left``\\ , ``center`` or ``right``
        :param anchor_y: either ``bottom``\\ , ``center`` or ``top``
        :return: LayoutCell subclass
        """
        return _GridCell(self.peng, self, pos, size, anchor_x, anchor_y, border)


class LayoutCell(object):
    """
    Base Layout Cell.

    Not to be used directly. Usually subclasses of this class are returned by layouts.

    Instances can be passed to Widgets as the ``pos`` argument. The ``size`` argument will
    be automatically overridden.

    Note that manually setting ``size`` will override the size set by the layout cell,
    though the position will be kept.
    """
    @property
    def pos(self):
        """
        Property accessing the position of the cell.

        This usually refers to the bottom-left corner, but may change depending on arguments
        passed during creation.

        Note that results can be floats.

        :return: 2-tuple of ``(x,y)``
        """
        raise NotImplementedError("pos property has to be overridden")

    @property
    def size(self):
        """
        Property accessing the size of the cell.

        Note that results can be floats.

        :return: 2-tuple of ``(width, height)``
        """
        raise NotImplementedError("size property has to be overridden")


class DumbLayoutCell(LayoutCell):
    """
    Dumb layout cell that behaves like a widget.

    Note that this class is not actually widget and should only be used as the ``pos``
    argument to a widget or the ``parent`` to another Layout.

    It can be used to create, for example, a :py:class:`GridLayout()` over only a portion
    of the screen.

    Even though setting the :py:attr:`pos` and :py:attr:`size` attributes is possible,
    sometimes a redraw cannot be triggered correctly if e.g. the parent is not submenu.
    """
    def __init__(self, parent, pos, size):
        self.parent = parent
        self._pos = pos
        self._size = size

    @property
    def pos(self):
        """
        Property that will always be a 2-tuple representing the position of the widget.

        Note that this method may call the method given as ``pos`` in the initializer.

        The returned object will actually be an instance of a helper class to allow for setting only the x/y coordinate.

        This property also respects any :py:class:`Container` set as its parent, any offset will be added automatically.

        Note that setting this property will override any callable set permanently.
        """
        if isinstance(self._pos, list) or isinstance(self._pos, tuple):
            r = self._pos
        elif callable(self._pos):
            w, h = self.parent.size[:]
            r = self._pos(w, h, *self.size)
        elif isinstance(self._pos, LayoutCell):
            r = self._pos.pos
        else:
            raise TypeError("Invalid position type")

        ox, oy = self.parent.pos
        r = r[0] + ox, r[1] + oy

        # if isinstance(self.submenu,ScrollableContainer) and not self._is_scrollbar:# and self.name != "__scrollbar_%s"%self.submenu.name: # Widget inside scrollable container and not the scrollbar
        #    r = r[0],r[1]+self.submenu.offset_y
        return WatchingList(r, self._wlredraw_pos)

    @pos.setter
    def pos(self, value):
        self._pos = value
        if hasattr(self.parent, "redraw"):
            self.parent.redraw()

    @property
    def size(self):
        """
        Similar to :py:attr:`pos` but for the size instead.
        """
        if isinstance(getattr(self, "_pos", None), LayoutCell):
            s = self._pos.size
        elif isinstance(self._size, list) or isinstance(self._size, tuple):
            s = self._size
        elif callable(self._size):
            w, h = self.parent.size[:]
            s = self._size(w, h)
        else:
            raise TypeError("Invalid size type")

        s = s[:]

        if s[0] == -1 or s[1] == -1:
            raise ValueError("Cannot set size to -1 in DumbLayoutCell")

        # Prevents crashes with negative size
        s = [max(s[0], 0), max(s[1], 0)]
        return WatchingList(s, self._wlredraw_size)

    @size.setter
    def size(self, value):
        self._size = value
        if hasattr(self.parent, "redraw"):
            self.parent.redraw()

    def _wlredraw_pos(self,wl):
        self._pos = wl[:]
        if hasattr(self.parent, "redraw"):
            self.parent.redraw()

    def _wlredraw_size(self,wl):
        self._size = wl[:]
        if hasattr(self.parent, "redraw"):
            self.parent.redraw()


class _GridCell(LayoutCell):
    def __init__(self, peng, parent, offset, size, anchor_x, anchor_y, border=1):
        self.peng = peng
        self.parent = parent
        self.offset = offset
        self._size = size

        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.border = border

    @property
    def pos(self):
        dx, dy = self.parent.bordersize
        dx *= self.border
        dy *= self.border

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
        elif self.anchor_y == "top":
            y = py+oy+sy-dy/2
        else:
            raise ValueError(f"Invalid anchor_y of {self.anchor_y}")

        return x, y

    @property
    def size(self):
        dx, dy = self.parent.bordersize
        csx, csy = self.parent.cell_size  # Cell size in px
        sxc, sxy = self._size  # Size in cells
        sx, sy = sxc * csx-dx*self.border, sxy * csy-dy*self.border

        return sx, sy
