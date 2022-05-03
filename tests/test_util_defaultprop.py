#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util_defaultprop.py
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

import pytest

from peng3d.util import default_property


def test_defprop_decorator():
    class A:
        @default_property("parent")
        def attr(self):
            ...

    class B:
        attr = "B"

    a = A()
    b = B()
    a.parent = b

    # Basics
    assert a.attr == "B"
    assert a.attr == b.attr
    assert not hasattr(a, "_attr")

    # Change parent attribute
    b.attr = "C"
    assert a.attr == "C"

    # Change child attribute
    a.attr = "A"
    assert a.attr == "A"
    assert a._attr == "A"
    assert b.attr == "C"

    # Reset child attribute via None
    a.attr = None
    assert b.attr == "C"
    assert a.attr == "C"

    # Set child attribute
    a.attr = b
    assert a.attr == b

    # Reset child attribute via del
    del a.attr
    assert a.attr == "C"
    assert b.attr == "C"
    assert not hasattr(a, "_attr")

    # Try double-delete
    del a.attr
    assert a.attr == "C"
    assert not hasattr(a, "_attr")

    # Manually set _attr
    a._attr = "D"
    assert a.attr == "D"
    assert b.attr == "C"


def test_defprop_docstring():
    class A:
        @default_property("parent")
        def attr(self):
            """Docstring"""
            ...

    # Should have been copied through
    assert A.attr.__doc__ == "Docstring"


def test_defprop_classattr():
    class A:
        attr = default_property("parent", "attr")

    class B:
        attr = "B"

    a = A()
    b = B()
    a.parent = b

    # Base case
    assert a.attr == "B"
    assert a.attr == b.attr

    # Change of child
    a.attr = "A"
    assert a.attr == "A"
    assert b.attr == "B"

    # Reset and change of parent attr
    del a.attr
    b.attr = "C"
    assert a.attr == "C"
    assert a.attr == b.attr


def test_defprop_parent_attr():
    class A:
        @default_property("parent", parent_attr="a")
        def attr(self):
            ...

    class B:
        a = "B"

    a = A()
    b = B()
    a.parent = b

    assert a.attr == "B"
    assert a.attr == b.a

    # Change child attr
    a.attr = "A"
    assert a.attr == "A"
    assert b.a == "B"
    assert a._attr == "A"  # Ensure correct name of internal attribute


def test_defprop_wrongdec():
    with pytest.raises(TypeError) as excinfo:

        class A:
            @default_property
            def attr(self):
                ...

    assert "decorator" in str(excinfo.value)


def test_defprop_noname():
    class A:
        attr = default_property("parent")

    a = A()

    with pytest.raises(AttributeError) as excinfo:
        a.attr

    assert "Couldn't find parent" in str(excinfo.value)


def test_defprop_parenterr():
    class A:
        @default_property("parent")
        def attr(self):
            ...

        @default_property()
        def attr2(self):
            ...

    a = A()

    with pytest.raises(AttributeError) as excinfo:
        a.attr

    assert "Couldn't find parent" in str(excinfo.value)

    # Dummy object
    a.parent = object()

    with pytest.raises(AttributeError) as excinfo:
        a.attr

    assert "attribute within parent" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        a.attr2

    assert "PARENT_ATTR" in str(excinfo.value)


def test_defprop_autoparent():
    class A:
        PARENT_ATTR = "parent"

        @default_property()
        def attr(self):
            ...

    class B:
        attr = "B"

    a = A()
    b = B()

    a.parent = b

    assert a.attr == "B"
    assert a.attr == b.attr
