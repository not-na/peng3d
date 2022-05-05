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

import collections
import inspect
from abc import ABCMeta, abstractmethod
from typing import (
    Dict,
    Type,
    TYPE_CHECKING,
    Optional,
    Union,
    Any,
    List,
    Set,
    overload,
    Callable,
    NamedTuple,
)

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


class StyleWatcher(NamedTuple):
    selector: str
    callback: Union[Callable[[StyleValue], Any], Callable[[], Any]]


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
    :py:attr:`Style.ATTRIBUTES`\\ . It is also not possible to access style attributes that
    start with an underscore or are methods of :py:class:`Style` this way. This access
    mode also supports read, write and delete accesses.

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

    ATTRIBUTES: List[str] = [
        "parent",
        "ATTRIBUTES",
    ]
    """
    Internal list of attributes that are reserved and cannot be used for styles via
    attribute access.
    
    This list may be extended in the future. Note that all attributes that start with an
    underscore are also implicitly reserved.
    """

    def __init__(
        self,
        parent: Optional[Union["Style", Dict[str, StyleValue]]] = None,
        overrides: Optional[Dict[str, StyleValue]] = None,
    ) -> None:
        self.parent = parent

        if isinstance(parent, Style):
            # Register with parent to be notified of changes
            parent._children.add(self)

        self._children: Set["Style"] = set()
        self._watchers: Set[StyleWatcher] = set()

        self._overrides: Dict[str, StyleValue] = util.default(overrides, {})

    def __getitem__(self, item: str) -> StyleValue:
        if item in self._overrides:
            return self._overrides[item]

        return self.parent[item]

    def __setitem__(self, key: str, value: StyleValue):
        oldval = self.get(key)
        contained = key in self
        self._overrides[key] = value

        if not contained or oldval != value:
            self._trigger_watchers(key, oldval)

    def __delitem__(self, key: str) -> None:
        # Only remove if overridden, reduces user code complexity
        if key in self._overrides:
            oldval = self._overrides[key]
            del self._overrides[key]

            if oldval != self[key]:
                self._trigger_watchers(key, oldval)

    def __contains__(self, item: str) -> bool:
        return item in self._overrides or item in self.parent

    def __getattr__(self, item: str) -> StyleValue:
        return self[item]

    def __setattr__(self, key: str, value) -> None:
        if (
            key[0] == "_" or key in self.ATTRIBUTES
        ):  # We use key[0] == "_" because it much faster (over 3x)
            super().__setattr__(key, value)
        else:
            self[key] = value

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
            # self._overrides.update(_overrides)
            for key, val in _overrides.items():
                if key not in kwargs:  # To prevent double triggers
                    oldval = self._overrides[key]
                    self._overrides[key] = val
                    if oldval != val:
                        self._trigger_watchers(key, oldval)

        # self._overrides.update(kwargs)
        for key, val in kwargs.items():
            oldval = self._overrides[key]
            self._overrides[key] = val
            if oldval != val:
                self._trigger_watchers(key, oldval)

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

    def get(
        self, key: str, default: Optional[StyleValue] = None
    ) -> Optional[StyleValue]:
        """
        Returns the effective value of the given key or the given default if it couldn't
        be found.
        """
        if key in self._overrides:
            return self._overrides[key]
        return self.parent.get(key, default)

    @overload
    def add_watcher(self, watcher: StyleWatcher) -> None:
        pass

    @overload
    def add_watcher(
        self,
        selector: str,
        callback: Union[Callable[[StyleValue], Any], Callable[[], Any]],
    ) -> None:
        pass

    def add_watcher(self, watch_sel, callback=None):
        """
        Adds a watcher for specific changes in local styles.

        Watchers can be used to automatically update widgets or other visual elements
        whenever the effective value of a style attribute changes. This includes scenarios
        where the (not locally overridden) style attribute of the parent changes, causing
        a change in the effective local value.

        The watcher system tries its best to remove unnecessary triggers and double-triggers,
        but they may still occur under some circumstances. Thus, it is recommended to
        only use (semi-)idempotent functions as callbacks. A popular example for a suitable
        callback would be the `redraw()` method of widgets, since it will only queue
        the actual redraw and thus prevents extraneous redraws.

        This method accepts either an instance of :py:class:`StyleWatcher` or a selector
        string followed by a callback function.

        Selectors are strings that describe what changes to listen to. Currently, selectors
        are quite rudimentary, but it is planned to add a more sophisticated system later.

        The special ``*`` selector matches all changes and will thus be triggered on any
        change of any local attribute.

        Alternatively, all other strings will trigger on the change of a style attribute
        with their exact name.

        Callback functions can either take no arguments or the old value of the style
        attribute as a single argument.
        """
        if isinstance(watch_sel, StyleWatcher):
            sw = watch_sel
        elif isinstance(watch_sel, str) and callback is not None:
            sw = StyleWatcher(watch_sel, callback)
        else:
            raise TypeError("Invalid argument combination to add_watcher()")

        sig = inspect.signature(sw.callback)
        if len(sig.parameters) > 1:
            raise TypeError(
                f"Callback function must have exactly zero or one parameters, not {len(sig.parameters)}!"
            )
        # Does not cover the case of a single keyword-only argument, which would pass the
        # check, but cause an error at callback-time. Such functions are relatively unusual
        # and thus not checked for

        self._watchers.add(sw)

    def _trigger_watchers(
        self, key: str, oldval: StyleValue, from_parent: Optional[bool] = False
    ):
        if from_parent and (oldval == self.get(key) or key not in self):
            # Skip if parent change is irrelevant for us
            # Could be either due to a local override or override in some intermediary
            return

        for selector, callback in self._watchers:
            match = (selector == key) or (selector == "*")

            # TODO: extend selector features

            if match:
                sig = inspect.signature(callback)
                if len(sig.parameters) == 1:
                    callback(oldval)
                elif len(sig.parameters) == 0:
                    callback()
                else:
                    # Should have been caught earlier already, but just in case
                    raise TypeError("Invalid callback")

        for child in self._children:
            child._trigger_watchers(key, oldval, from_parent=True)


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
