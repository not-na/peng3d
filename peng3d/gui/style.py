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
    "Style",
    "DEFAULT_STYLE",
]

from abc import ABCMeta, abstractmethod
from typing import Dict, Type, TYPE_CHECKING, Optional, Union, Any, List

from .. import util
from ..util.types import *

if TYPE_CHECKING:
    from . import widgets


class _BorderstyleMetaclass(ABCMeta):
    def __new__(mcls, clsname, bases, attrs, name: Optional[str] = None, **kwargs):
        # if name is None:
        #    raise TypeError(
        #        "Border styles require a 'name' keyword argument in the class definition"
        #    )
        mcls.name = name

        # attrs["__eq__"] = mcls.__eq__
        # attrs["name"] = name
        return super(_BorderstyleMetaclass, mcls).__new__(
            mcls, clsname, bases, attrs, **kwargs
        )

    def __eq__(self, other):
        if self.name is not None:
            return other == self.name or self is other
        else:
            return self is other

    def __hash__(self):
        return hash((self.name, self.__name__))


class Borderstyle(object, metaclass=_BorderstyleMetaclass):
    """
    Base class for all border styles.

    Each border style class serves a single style, although some parameters may be adjustable.

    Currently, border style classes are not instantiated per widget, but rather rely on
    class methods. This reduces memory overhead but may be changed in the future.

    For backwards compatibility, border style classes themselves compare equal with their
    old-style string equivalents. This is accomplished with a metaclass and not necessary
    to emulate for new styles and may be removed in a future version.
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


class FlatBorder(Borderstyle, name="flat"):
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


class GradientBorder(Borderstyle, name="gradient"):
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


class OldshadowBorder(Borderstyle, name="oldshadow"):
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


class MaterialBorder(Borderstyle, name="material"):
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


class Style(object):
    """
    Core of the hierarchical style system.

    This class allows for easily inheriting styles from a parent (e.g. submenu or menu)
    while allowing dynamic overwriting at any level in the hierarchy. For example, a
    specific submenu could have a different font that would then be automatically applied
    to all widgets within it, unless the font was overridden for the widget locally.

    When reading a style attribute, this class first checks if it has a local override for
    that attribute. If so, it will be returned. If the attribute wasn't overridden locally,
    the parent is queried and its result returned. The root of this hierarchy is the
    :py:attr:`~peng3d.peng.Peng.style` attribute of the :py:class:`~peng3d.peng.Peng()`
    singleton, which uses the styles defined in :py:data:`DEFAULT_STYLE` as a default.
    If a style attribute is not found anywhere, a :py:exc:`KeyError` will be raised.

    When writing a style attribute, a local override is created. This causes all subsequent
    accesses to the style attribute within this instance and all children (e.g. widgets
    within a submenu) to read back the new value. Deleting the style attribute will reset
    this override and thus reset the read value back to the parent value.

    Note that changes in an attribute usually require a redraw of the affected widgets.
    If a redraw is not performed, weird graphical glitches may happen.

    This class is very flexible and allows several different modes of access.

    First, it is possible to use it like a dict, e.g. ``style["font"]``\\ . It is possible
    to read, write and delete using this method. All styles are accessible in this manner
    and arbitrary strings are allowed as keys, though it is recommended to stick to valid
    Python identifiers.

    For convenience, it is also possible to access style attributes as literal attributes
    of a :py:class:`Style` instance, e.g. ``style.font``\\ . Note that this only allows
    accesses to style attributes whose name is a valid python identifier and that are
    not in the list of reserved attributes, stored in the class attribute
    :py:attr:`Style.ATTRIBUTES`\\ . This access mode also supports read, write and delete
    accesses.

    Note that unlike the helpers :py:class:`~peng3d.util.default_property` and
    :py:class:`~peng3d.util.default`\\ , :py:class:`Style` does not reset an override
    if a write with a value of ``None`` is performed.
    """

    parent: Union["Style", Dict[str, StyleValue]]
    """
    Attribute that stores the parent of this style.
    
    May be changed during runtime, though most widgets will require a redraw to fully
    respect changed effective style values.
    
    It is usually not required to write to this attribute, since widgets do not currently
    support being moved between different submenus or even menus.
    """

    ATTRIBUTES: List[str] = ["parent", "_overrides", "ATTRIBUTES"]
    """
    Internal list of attributes that are reserved and cannot be used for styles via
    attribute access.
    """

    def __init__(
        self,
        parent: Optional[Union["Style", Dict[str, StyleValue]]] = None,
        overrides: Optional[Dict[str, StyleValue]] = None,
    ) -> None:
        self.parent = parent

        self._overrides: Dict[str, StyleValue] = util.default(overrides, {})

    def __getitem__(self, item: str) -> StyleValue:
        if item in self._overrides:
            return self._overrides[item]

        return self.parent[item]

    def __setitem__(self, key: str, value: StyleValue):
        self._overrides[key] = value

    def __delitem__(self, key: str) -> None:
        # Only remove if overridden, reduces user code complexity
        if key in self._overrides:
            del self._overrides[key]

    def __contains__(self, item: str) -> bool:
        return item in self._overrides or item in self.parent

    def __getattr__(self, item: str) -> StyleValue:
        return self[item]

    def __setattr__(self, key: str, value) -> None:
        if key in self.ATTRIBUTES:
            super().__setattr__(key, value)
        else:
            self._overrides[key] = value

    def update(
        self, _overrides: Optional[Dict[str, StyleValue]] = None, **kwargs
    ) -> None:
        """
        Updates several style attributes at the same time.

        Note that this method only supports creating and modifying overrides. Keys not
        present in the given data will be kept as is.

        This method supports both passing in a dictionary and passing in keyword attributes.
        Note that in the case of a style attribute being present in both the dictionary
        and a keyword argument, the keyword argument takes precedence.

        :param _overrides: Optional dictionary to add/modify overrides from
        :type _overrides: Optional[Dict[str, StyleValue]]
        :param kwargs: Optional keyword arguments to add/modify overrides from
        :type kwargs: StyleValue
        :return: None
        :rtype: None
        """
        if _overrides is not None:
            self._overrides.update(_overrides)
        self._overrides.update(kwargs)

    def is_overridden(self, key: str) -> bool:
        """
        Checks whether a given key is currently being overridden.

        If this returns true, any change in parent styles will not affect the value
        of the given style attribute.

        :param key: Key to check
        :type key: str
        :return: whether key is currently overridden
        :rtype: bool
        """
        return key in self._overrides

    def override_if_not_none(self, key: str, value: Optional[StyleValue]) -> None:
        """
        Overrides the given key if the provided value is not ``None``\\ .

        This helper allows for easy style overriding via keyword arguments. Simply create
        a keyword argument in the constructor of an object that uses styles and set the
        default of that keyword argument to ``None``\\ . In the constructor, you can then
        call this function like so::

            self.style.override_if_not_none("font", font)

        Note that this method is unsuitable for style attributes that may actually want
        to have a value of ``None``\\ .

        :param key: Key to override
        :type key: str
        :param value: value used to override if it is not ``None``
        :type value: Optional[StyleValue]
        :return: None
        :rtype: None
        """
        if value is not None:
            self[key] = value


DEFAULT_STYLE: Dict[str, StyleValue] = {
    "font": "Arial",
    "font_size": 16,
    "font_color": (62, 67, 73, 255),
    "border": (4, 4),
    "borderstyle": FlatBorder,
}
"""
Default styles for all parts of peng3d.

These styles represent a sensible default for common use cases.

For application-wide changes, it is recommended to override the styles in question using
the :py:attr:`peng3d.peng.Peng.style` attribute.
"""
