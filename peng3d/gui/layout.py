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

__all__ = ["Layout", "GridLayout", "LayoutCell", "ResponsiveLayout", "BREAKPOINTS"]

from typing import Optional, Dict, Union, OrderedDict, Tuple, List

import peng3d
from peng3d import util
from peng3d.util import WatchingList, calculated_from

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass  # Headless mode


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
    @calculated_from("size", "res")
    def cell_size(self):
        """
        Helper property defining the current size of cells in both x and y axis.

        :return: 2-tuple of float
        """
        return self.size[0] / self.res[0], self.size[1] / self.res[1]

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

    def _wlredraw_pos(self, wl):
        self._pos = wl[:]
        if hasattr(self.parent, "redraw"):
            self.parent.redraw()

    def _wlredraw_size(self, wl):
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

        px, py = self.parent.pos  # Parent position in px
        oxc, oyc = self.offset  # Offset in cells
        csx, csy = self.parent.cell_size  # Cell size in px
        ox, oy = oxc * csx, oyc * csy  # Offset in px

        sxc, sxy = self._size  # Size in cells
        sx, sy = sxc * csx, sxy * csy  # Size in px

        if self.anchor_x == "left":
            x = px + ox + dx / 2
        elif self.anchor_x == "center":
            x = px + ox + sx / 2
        elif self.anchor_x == "right":
            x = px + ox + sx - dx / 2
        else:
            raise ValueError(f"Invalid anchor_x of {self.anchor_x}")

        if self.anchor_y == "bottom":
            y = py + oy + dy / 2
        elif self.anchor_y == "center":
            y = py + oy + sy / 2
        elif self.anchor_y == "top":
            y = py + oy + sy - dy / 2
        else:
            raise ValueError(f"Invalid anchor_y of {self.anchor_y}")

        return x, y

    @property
    def size(self):
        dx, dy = self.parent.bordersize
        csx, csy = self.parent.cell_size  # Cell size in px
        sxc, sxy = self._size  # Size in cells
        sx, sy = sxc * csx - dx * self.border, sxy * csy - dy * self.border

        return sx, sy


BREAKPOINTS = {
    # Bootstrap breakpoints
    "xs": 0,
    "sm": 576,
    "md": 768,
    "lg": 992,
    "xl": 1200,
    "xxl": 1400,
    # Common screen resolutions
    "vga": 640,  # AKA 640p
    "hd": 720,  # AKA 720p
    "fhd": 1920,  # AKA 1080p
    "qhd": 2560,  # AKA 1440p
    "uhd": 3840,  # AKA 4k/2160p
}


class ResponsiveLayout(Layout):
    def __init__(self, peng, parent, cols: int = 12):
        super().__init__(peng, parent)

        self.cols: int = cols
        self.rows: Dict[Union[str, int], "_ResponsiveRow"] = {}

    def row(
        self, name: Optional[Union[str, int]] = None, height: Optional[float] = None
    ) -> "_ResponsiveRow":
        if name is None:
            name = 0
            while name in self.rows:
                name += 1

        if name not in self.rows:
            self.rows[name] = _ResponsiveRow(self, name, height)

        return self.rows[name]


class _ResponsiveRow(object):
    def __init__(
        self, layout: ResponsiveLayout, name: Union[str, int], height: Optional[float]
    ):
        self.layout: ResponsiveLayout = layout
        self.name = name
        self._height = height

        self.cols: Dict[Union[str, int], "_ResponsiveCol"] = {}

    def col(
        self, name: Optional[Union[str, int]] = None, **kwargs: float
    ) -> "_ResponsiveCol":
        if name is None:
            name = 0
            while name in self.cols:
                name += 1

        if name not in self.cols:
            self.cols[name] = _ResponsiveCol(self.layout, self, name, kwargs)

        # Invalidate layout cache whenever a new col is added
        calculated_from.clear_cache(self, "col_layout")

        return self.cols[name]

    @property
    @calculated_from("layout.cols", "layout.size")
    # NOTE: self.cols is not in dependencies
    def col_layout(
        self,
    ) -> Tuple[
        Tuple[Tuple[Tuple[float, float, Union[str, int]], ...], ...],
        Dict[Union[str, int], Tuple[int, float, float]],
    ]:
        rows = []
        cur_row = []
        cols_in_row = 0
        cols = {}

        for name, col in self.cols.items():
            col_width = col.col_width
            if cols_in_row + col_width <= self.layout.cols:
                # Fits in the current row, add it
                cols_in_row += col_width
                cur_row.append((col_width, name))
            else:
                # Doesn't fit, calculate out the current row and start a new one
                rows.append(self._calc_row(cur_row, cols_in_row, cols, rows))

                cols_in_row = col_width
                cur_row = [(col_width, name)]

        if len(cur_row) > 0:
            rows.append(self._calc_row(cur_row, cols_in_row, cols, rows))

        return tuple(rows), cols

    def _calc_row(self, cur_row, cols_in_row, cols, rows):
        out_row = []
        cur_perc = 0.0
        for cw, n in cur_row:
            perc = cw / cols_in_row
            out_row.append((cur_perc, cur_perc + perc, n))
            cols[n] = (len(rows), cur_perc, cur_perc + perc)
            cur_perc += perc

        return tuple(out_row)

    @property
    def base_pos(self) -> Tuple[float, float]:
        bx, by = self.layout.pos

        x = bx

        rows = list(self.layout.rows.values())
        upper_height = sum(
            r.height * len(r.col_layout[0]) for r in rows[: rows.index(self)]
        )
        y = self.layout.size[1] + by - upper_height

        return x, y

    @property
    def height(self) -> float:
        if self._height is not None:
            return self._height

        # TODO: auto-determine height
        raise NotImplementedError("Auto-height is not yet supported")


class _ResponsiveCol(LayoutCell):
    def __init__(
        self,
        layout: ResponsiveLayout,
        row: _ResponsiveRow,
        name: Union[str, int],
        sizes: Dict[str, float],
    ):
        self.layout = layout
        self.row: _ResponsiveRow = row
        self.name = name
        self.sizes = sizes

    @property
    def sizes(self) -> Dict[str, float]:
        return self._sizes

    @sizes.setter
    def sizes(self, val):
        # Validate given breakpoints and their sizes
        for bp, size in val.items():
            if bp not in BREAKPOINTS:
                raise ValueError(
                    f"Invalid breakpoint, '{bp}' is not a known breakpoint!"
                )
            if size > self.layout.cols:
                raise ValueError(
                    "A responsive column cannot have a size larger than the total amount of columns"
                )

        # Clear col_width cache and update internal copy
        self._sizes = val
        calculated_from.clear_cache(self, "col_width")

    @property
    @calculated_from("layout.size")
    # NOTE: _sizes not in dependencies, since sizes invalidates the cache of this property whenever it is changed
    def col_width(self) -> float:
        width = self.layout.size[0]

        out = None
        # Find the largest breakpoint that is still larger or equal to the width
        for bp in self._sizes.keys():
            if width >= BREAKPOINTS[bp] and (
                out is None or BREAKPOINTS[bp] >= BREAKPOINTS[out]
            ):
                out = bp

        if out is None:
            return 1
        return self._sizes[out]

    @property
    # @calculated_from("row.col_layout", "row.base_pos", "row.height", "layout.size")
    def pos(self) -> Tuple[float, float]:
        rows, cols = self.row.col_layout
        row, start, end = cols[self.name]

        bx, by = self.row.base_pos

        x = bx + start * self.layout.size[0]
        y = (
            by - (row + 1) * self.row.height
        )  # TODO: add support for per-subrow dynamic height

        return x, y

    @property
    # @calculated_from("row.col_layout", "row.height", "layout.size")
    def size(self) -> Tuple[float, float]:
        rows, cols = self.row.col_layout
        row, start, end = cols[self.name]

        return self.layout.size[0] * (end - start), self.row.height
