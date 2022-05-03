#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#
#  Copyright 2017-2022 notna <notna@apparat.org>
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

__all__ = [
    "WatchingList",
    "register_pyglet_handler",
    "ActionDispatcher",
    "SmartRegistry",
    "default",
    "default_property",
]

import sys
import weakref
import threading
from typing import Callable, Tuple, List, Dict, Optional, Union, Any, TypeVar

try:
    import bidict
except ImportError:
    HAVE_BIDICT = False
else:
    HAVE_BIDICT = True

from .gui import *


T = TypeVar("T")


def default(arg: Optional[T], _default: T) -> T:
    """
    Small helper function that replaces the given argument with a default if the argument
    is ``None``\\ .

    This can also be written as a ternary expression in-line, but using this function
    makes the purpose clearer and easier to read.
    """
    return arg if arg is not None else _default


class default_property(object):
    """
    Special property decorator/class that allows for easy defaulting of attributes to
    the parents' attributes.

    This class can either be used as a decorator or as a class attribute.

    For decorator usage, simply decorate an empty method with the name of the attribute to
    default, passing the name of the attribute the parent is stored in::

        class A:
            @default_property("parent")
            def my_attr(self): ...

    Accessing ``my_attr`` will then return the value of the ``my_attr`` attribute of the
    ``parent`` attribute of the class instance. Setting ``my_attr`` will not touch the
    attribute of the same name of the parent, but rather set an internal attribute, causing
    all subsequent accesses to return this local attribute.

    Setting the property to ``None`` will reset the whole mechanism, causing all accesses
    until the next write to return the defaulted value.

    Internally, all this is handled by a shadow attribute with the same name as the
    actual property, but prefixed by an underscore. This internal attribute may also
    be written to directly, which is especially useful in constructors.

    Deleting the property will also just reset it, until it is next written.

    Alternatively, this class can also be used as a class attribute, for the same effect
    as described above::

        class A:
            my_attr = default_property("parent")

    Note that this only works if the property is defined in the class body. Later
    assignment to the class object is possible, but requires providing the ``name`` argument,
    since auto-detecting the attribute name is then not possible.

    To simplify creation, it is possible to set the ``PARENT_ATTR`` class attribute to
    provide a default first argument to :py:class:`default_property`\\ . This is usually
    worthwhile if multiple ``default_properties`` are used within the same class hierarchy,
    especially since the class attribute value can be inherited.

    The ``parent_attr`` keyword-only argument may be passed to override what attribute
    of the parent is used as a default.
    """

    def __init__(
        self,
        parent: Optional[str] = None,
        name: Optional[str] = None,
        *,
        parent_attr: Optional[str] = None
    ):
        if callable(parent):  # Catch common error
            raise TypeError(
                "parent argument is callable, but should be a string. "
                "Likely due to incorrect usage as a decorator"
            )

        self.name = name
        self.parent = parent
        self.parent_attr = default(parent_attr, name)

    def __call__(self, func):
        if self.name is None:
            self.name = func.__name__

            if self.parent_attr is None:
                self.parent_attr = self.name

        self.__doc__ = func.__doc__
        return self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        if self.name is None:
            raise TypeError(
                "Missing required argument 'name' if not used as a decorator"
            )

        if (self.parent is None and not hasattr(instance, "PARENT_ATTR")) or (
            self.parent is None
            and hasattr(instance, "PARENT_ATTR")
            and not isinstance(instance.PARENT_ATTR, str)
        ):
            raise TypeError(
                "Missing required argument 'parent' if object has no 'PARENT_ATTR' string attribute"
            )
        if self.parent is None:
            self.parent = instance.PARENT_ATTR

        if getattr(instance, "_" + self.name, None) is not None:
            return getattr(instance, "_" + self.name)

        if not hasattr(instance, self.parent):
            raise AttributeError("Couldn't find parent to default to")
        elif not hasattr(getattr(instance, self.parent), self.parent_attr):
            raise AttributeError("Couldn't find attribute within parent to default to")

        return getattr(getattr(instance, self.parent), self.parent_attr)

    def __set__(self, instance, value):
        setattr(instance, "_" + self.name, value)

    def __delete__(self, instance):
        if hasattr(instance, "_" + self.name):
            delattr(instance, "_" + self.name)

    def __set_name__(self, owner, name):
        self.name = name

        if self.parent_attr is None:
            self.parent_attr = self.name


class WatchingList(list):
    """
    Subclass of :py:func:`list` implementing a watched list.

    A WatchingList will call the given callback with a reference to itself whenever it is modified.
    Internally, the callback is stored as a weak reference, meaning that the creator should keep a reference around.

    This class is used in :py:class:`peng3d.gui.widgets.BasicWidget()` to allow for modifying single coordinates of the pos and size properties.
    """

    def __init__(self, l, callback=None):
        if callback is not None:
            if hasattr(callback, "__self__"):
                self.callback = weakref.WeakMethod(callback)
            else:
                self.callback = weakref.ref(callback)
        else:
            self.callback = None
        super(WatchingList, self).__init__(l)

    def __setitem__(self, *args):
        super(WatchingList, self).__setitem__(*args)
        if self.callback is not None:
            self.callback()(self)


def register_pyglet_handler(peng, func, event, raiseErrors=False):
    """
    Registers the given pyglet-style event handler for the given pyglet event.

    This function allows pyglet-style event handlers to receive events bridged
    through the peng3d event system. Internally, this function creates a lambda
    function that decodes the arguments and then calls the pyglet-style event handler.

    The ``raiseErrors`` flag is passed through to the peng3d event system and will
    cause any errors raised by this handler to be ignored.

    .. seealso::
       See :py:meth:`~peng3d.peng.Peng.addEventListener()` for more information.
    """
    peng.addEventListener(
        "pyglet:%s" % event, (lambda data: func(*data["args"])), raiseErrors
    )


class ActionDispatcher(object):
    """
    Helper Class to be used to enable action support.

    Actions are simple callbacks that are specific to the instance they are registered with.

    To be able to use actions, a class must be a subclass of :py:class:`ActionDispatcher()`\\ .

    Creation of required data structures is handled automatically when the first action is added.

    Internally, this object uses the ``actions`` attribute to store a map of action names to
    a list of callbacks.
    """

    actions: Dict[str, List[Tuple[Callable, tuple, dict]]]

    def addAction(self, action: str, func: Callable, *args, **kwargs):
        """
        Adds a callback to the specified action.

        All other positional and keyword arguments will be stored and passed to the function upon activation.
        """
        if not hasattr(self, "actions"):
            self.actions = {}
        if action not in self.actions:
            self.actions[action] = []
        self.actions[action].append((func, args, kwargs))

    def doAction(self, action: str):
        """
        Helper method that calls all callbacks registered for the given action.
        """
        if not hasattr(self, "actions"):
            return
        for f, args, kwargs in self.actions.get(action, []):
            f(*args, **kwargs)


class SmartRegistry(object):
    """
    Smart registry allowing easy management of mappings from int to str and vice versa.

    Note that bidict is required to be able to use this class.

    ``data`` may be a dictionary to initialize the registry with. Only dictionaries
    gotten from the :py:attr:`data` property should be used.

    ``reuse_ids`` specifies whether or not the automatic ID generator should re-use
    old, now unused IDs. See :py:meth:`genNewID()` for more information.

    ``start_id`` is the lowest ID that will be generated by the automatic ID generator.

    ``max_id`` is the highest ID that will be generated by the automatic ID generator.
    Should this limit by reached, an :py:exc:`AssertionError` will be raised.

    ``default_reg`` may be a dictionary mapping IDs to names. It will only be used if
    ``data`` did not already contain a registry.

    It is possible to access the registry via the dict-style ``reg[key]`` notation.
    This will return the name of whatever object was used as the key.

    Registering is also possible in a similar manner, like ``reg[name]=id``\\ .
    ``id`` may be ``None`` to automatically generate one.

    This class also supports the ``in`` operator, note that both IDs and names are checked.
    """

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        reuse_ids: bool = False,
        start_id: int = 0,
        max_id: Optional[int] = None,
        default_reg: Optional[Dict] = None,
    ):
        # TODO: fix max_id being a float by default
        assert HAVE_BIDICT

        self._data = default(data, {})

        self.reuse_ids: bool = reuse_ids
        # if true, new ids will be assigned from lowest available id
        # if false, an internal counter is used

        self.start_id: int = start_id
        self.max_id: Union[float, int] = max_id

        self.id_lock = threading.Lock()
        self.registry_lock = threading.Lock()

        if "reg" not in self._data:
            default_reg = default(default_reg, {})
            if not isinstance(default_reg, dict):
                raise TypeError("Default Registry must be a dictionary")
            # no reg yet, create a new one
            # ID->NAME mapping
            self._data["reg"] = default_reg

        for k in self._data["reg"].keys():
            if not isinstance(k, int):
                raise TypeError("All keys must be integers")

        for v in self._data["reg"].values():
            if not isinstance(v, str):
                raise TypeError("All values must be strings")

        self._data["reg"] = bidict.bidict(self._data["reg"])
        print(self._data["reg"])

        if not self.reuse_ids and "next_id" not in self._data:
            if self._data.get("reg", {}) != {}:
                # already data there, find highest id +1
                self._data["next_id"] = max(max(self._data["reg"].keys()) + 1, start_id)
            else:
                # no data there, use start_id
                self._data["next_id"] = self.start_id

        print(self._data)

    def genNewID(self) -> int:
        """
        Generates a new ID.

        If ``reuse_ids`` was false, the new ID will be read from an internal counter
        which is also automatically increased. This means that the newly generated ID is already reserved.

        If ``reuse_ids`` was true, this method starts counting up from ``start_id`` until it finds an
        ID that is not currently known. Note that the ID is not reserved, this means that
        calling this method simultaneously from multiple threads may cause the same ID to be returned twice.

        Additionally, if the ID is greater or equal to ``max_id``\\ , an :py:exc:`AssertionError` is raised.
        """
        if self.reuse_ids:
            i = self.start_id
            while True:
                if i not in self._data["reg"]:
                    assert self.max_id is None or i <= self.max_id
                    return i  # no need to change any variables
                i += 1
        else:
            with self.id_lock:
                # new id creation in lock, to avoid issues with multiple threads
                i = self._data["next_id"]
                assert self.max_id is None or i <= self.max_id
                self._data["next_id"] += 1
            return i

    def register(self, name: str, force_id: Optional[int] = None) -> int:
        """
        Registers a name to the registry.

        ``name`` is the name of the object and must be a string.

        ``force_id`` can be optionally set to override the automatic ID generation
        and force a specific ID.

        Note that using ``force_id`` is discouraged, since it may cause problems when ``reuse_ids`` is false.
        """
        with self.registry_lock:
            if force_id is None:
                new_id = self.genNewID()
            else:
                new_id = force_id
            self._data["reg"][new_id] = name
            return new_id

    def deregister(self, key: Union[int, str]) -> None:
        del self._data["reg"][self.normalizeID(key)]

    def normalizeID(self, in_id: Union[int, str]) -> int:
        """
        Takes in an object and normalizes it to its ID/integer representation.

        Currently, only integers and strings may be passed in, else a :py:exc:`TypeError`
        will be thrown.
        """
        if isinstance(in_id, int):
            assert in_id in self._data["reg"]
            return in_id
        elif isinstance(in_id, str):
            assert in_id in self._data["reg"].inv
            return self._data["reg"].inv[in_id]
        else:
            raise TypeError("Only int and str can be converted to IDs")

    def normalizeName(self, in_name: Union[int, str]) -> str:
        """
        Takes in an object and normalizes it to its name/string.

        Currently, only integers and strings may be passed in, else a :py:exc:`TypeError`
        will be thrown.
        """
        if isinstance(in_name, str):
            assert in_name in self._data["reg"].inv
            return in_name
        elif isinstance(in_name, int):
            assert in_name in self._data["reg"]
            return self._data["reg"][in_name]
        else:
            raise TypeError("Only int and str can be converted to names")

    @property
    def data(self) -> Dict[str, Any]:
        """
        Read-only property to access the internal data.

        This is a dictionary containing all information necessary to re-create the registry
        via the ``data`` argument.

        The returned object is fully JSON/YAML/MessagePack serializable, as it only contains
        basic python data types.
        """
        d = dict(self._data)
        d["reg"] = dict(d["reg"])
        return d

    def __getitem__(self, key: Union[int, str]) -> str:
        # to access registry as reg[obj] -> name
        return self.normalizeName(key)

    def __setitem__(self, key: str, value: Optional[int]) -> None:
        # None may be used as value for auto generation
        # to access registry as reg[name]=id
        self.register(key, value)

    def __delitem__(self, key: Union[int, str]):
        self.deregister(key)

    def __contains__(self, value: Union[int, str]) -> bool:
        return value in self._data["reg"] or value in self._data["reg"].inv
