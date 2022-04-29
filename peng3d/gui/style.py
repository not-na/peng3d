#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  style.py
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
    "Borderstyle",
    "FlatBorder",
    "GradientBorder",
    "OldshadowBorder",
    "MaterialBorder",
    "BORDERSTYLES",
    "norm_borderstyle",
]

from abc import ABCMeta, abstractmethod
from typing import Dict, Type, TYPE_CHECKING, Optional, Union

from ..util.types import *

if TYPE_CHECKING:
    from . import widgets


class Borderstyle(object, metaclass=ABCMeta):
    """
    Base class for all border styles.

    Each border style class serves a single style, although some parameters may be adjustable.

    Currently, border style classes are not instantiated per widget, but rather rely on
    class methods. This reduces memory overhead but may be changed in the future.
    """

    @classmethod
    @abstractmethod
    def get_colormap(
        cls,
        widget: "widgets.BasicWidget",
        bg: ColorRGB,
        o: ColorRGB,
        i: ColorRGB,
        s: ColorRGB,
        h: ColorRGB,
        state: Optional[str] = None,
    ):
        """
        Gets the color map for a button-style widget.

        TODO: document return format

        :param widget: Widget that the color map belongs to
        :type widget: BasicWidget
        :param bg: Background color this widget is placed on
        :type bg: ColorRGB
        :param o: Outer color, usually same as the background
        :type o: ColorRGB
        :param i: Inner color, usually lighter than the background
        :type i: ColorRGB
        :param s: Shadow color, usually quite a bit darker than the background
        :type s: ColorRGB
        :param h: Highlight color, usually quite a bit lighter than the background
        :type h: ColorRGB
        :param state: Optional widget state override
        :type state: str
        :return:
        :rtype:
        """
        pass


class FlatBorder(Borderstyle):
    @classmethod
    def get_colormap(
        cls,
        widget: "widgets.BasicWidget",
        bg: ColorRGB,
        o: ColorRGB,
        i: ColorRGB,
        s: ColorRGB,
        h: ColorRGB,
        state: Optional[str] = None,
    ):
        cb1 = i + i + i + i
        cb2 = i + i + i + i
        cb3 = i + i + i + i
        cb4 = i + i + i + i
        cc = i + i + i + i

        return cb1, cb2, cb3, cb4, cc


class GradientBorder(Borderstyle):
    @classmethod
    def get_colormap(
        cls,
        widget: "widgets.BasicWidget",
        bg: ColorRGB,
        o: ColorRGB,
        i: ColorRGB,
        s: ColorRGB,
        h: ColorRGB,
        state: Optional[str] = None,
    ):
        state = widget.getState() if state is None else state

        if state == "pressed":
            i = s
        elif state == "hover":
            i = [min(i[0] + 6, 255), min(i[1] + 6, 255), min(i[2] + 6, 255)]
        cb1 = i + i + o + o
        cb2 = i + o + o + i
        cb3 = o + o + i + i
        cb4 = o + i + i + o
        cc = i + i + i + i

        return cb1, cb2, cb3, cb4, cc


class OldshadowBorder(Borderstyle):
    @classmethod
    def get_colormap(
        cls,
        widget: "widgets.BasicWidget",
        bg: ColorRGB,
        o: ColorRGB,
        i: ColorRGB,
        s: ColorRGB,
        h: ColorRGB,
        state: Optional[str] = None,
    ):
        state = widget.getState() if state is None else state

        if state == "pressed":
            i = s
            s, h = h, s
        elif state == "hover":
            i = [min(i[0] + 6, 255), min(i[1] + 6, 255), min(i[2] + 6, 255)]
            s = [min(s[0] + 6, 255), min(s[1] + 6, 255), min(s[2] + 6, 255)]
        cb1 = h + h + h + h
        cb2 = s + s + s + s
        cb3 = s + s + s + s
        cb4 = h + h + h + h
        cc = i + i + i + i

        return cb1, cb2, cb3, cb4, cc


class MaterialBorder(Borderstyle):
    @classmethod
    def get_colormap(
        cls,
        widget: "widgets.BasicWidget",
        bg: ColorRGB,
        o: ColorRGB,
        i: ColorRGB,
        s: ColorRGB,
        h: ColorRGB,
        state: Optional[str] = None,
    ):
        state = widget.getState() if state is None else state

        if state == "pressed":
            i = [max(bg[0] - 20, 0), max(bg[1] - 20, 0), max(bg[2] - 20, 0)]
        elif state == "hover":
            i = [max(bg[0] - 10, 0), max(bg[1] - 10, 0), max(bg[2] - 10, 0)]
        cb1 = s + s + o + o
        cb2 = s + o + o + s
        cb3 = o + o + s + s
        cb4 = o + s + s + o
        cc = i + i + i + i

        return cb1, cb2, cb3, cb4, cc


BORDERSTYLES: Dict[str, Type[Borderstyle]] = {
    "flat": FlatBorder,
    "gradient": GradientBorder,
    "oldshadow": OldshadowBorder,
    "material": MaterialBorder,
}
"""
Map of border style names to classes that implement them.

See the documentation of each class for descriptions.
"""


def norm_borderstyle(borderstyle: Union[str, Type[Borderstyle]]) -> Type[Borderstyle]:
    """
    Normalizes border styles to :py:class:`Borderstyle` subclasses.

    :param borderstyle: Value to normalize
    :type borderstyle: Either str or Borderstyle subclass
    :return: Normalized value
    :rtype: Borderstyle subclass
    :raises TypeError: if an unexpected value was given
    """
    if isinstance(borderstyle, str):
        if borderstyle not in BORDERSTYLES:
            raise ValueError(f"Unknown border style {borderstyle}")
        return BORDERSTYLES[borderstyle]
    elif issubclass(borderstyle, Borderstyle):
        return borderstyle
    else:
        raise TypeError("Invalid border style!")
