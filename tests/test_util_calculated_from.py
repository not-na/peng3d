#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util_calculated_from.py
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

from peng3d.util import calculated_from


def test_single():
    class A:
        @property
        @calculated_from("b")
        def a(self):
            return self.b

    a = A()

    a.b = "a"
    assert a.a == a.b == "a"  # Cache miss
    assert a.a == "a"  # Cache hit

    a.b = None  # Special case none, ensure it is treated the same as any other value
    assert a.a is None  # Cache miss
    assert a.a is None  # Cache hit

    a.c = "c"  # Irrelevant attribute
    assert a.a is None


def test_multi():
    class A:
        @property
        @calculated_from("b", "c")
        def a(self):
            return [self.b, self.c]

    a = A()

    a.b = "b"
    a.c = "c"

    aa = a.a
    assert aa[0] == "b"
    assert aa[1] == "c"
    assert len(aa) == 2

    aa2 = a.a
    assert aa is aa2  # Should be exact same object, due to cache hit

    a.d = "d"
    # Ensure irrelevant attribute doesn't cause re-compute
    assert a.a is aa  # Important that we use identity check here, not equals


def test_nested():
    class A:
        @property
        @calculated_from("b.a", "c", "d.a")
        def a(self):
            return [self.b.a, self.c, self.d.a]

    class B:
        a = "A"

    a = A()
    a.b = B()
    a.d = B()

    a.c = "C"

    assert a.a[0] == a.b.a == "A"
    assert a.a[1] == a.c == "C"
    assert a.a[2] == a.d.a == "A"

    a.b.a = "A"
    a.c = "B"

    assert a.a[0] == a.b.a == "A"
    assert a.a[1] == a.c == "B"
    assert a.a[2] == a.d.a == "A"

    a.d.a = "C"

    assert a.a[0] == a.b.a == "A"
    assert a.a[1] == a.c == "B"
    assert a.a[2] == a.d.a == "C"

    # (Sub-) attribute is a list, special but common case
    a.b.a = [1, 2]
    assert a.a[0] is a.b.a
    assert a.a[0] == [1, 2]

    a.b.a = [3, 4]
    assert a.a[0] is a.b.a
    assert a.a[0] == [3, 4]


def test_method():
    class A:
        @calculated_from("b")
        def a(self):
            return self.b

    a = A()

    a.b = "a"
    assert a.a() == a.b == "a"
    assert a.a() == "a"

    a.b = "b"
    assert a.a() == a.b == "b"
    assert a.a() == "b"


def test_clear_cache():
    class A:
        @calculated_from("b")
        def a(self):
            return self.b + self.c

    a = A()

    a.b = "a"
    a.c = "a"
    assert a.a() == a.b + a.c == "aa"

    a.b = "b"
    assert a.a() == "ba"

    a.c = "b"
    assert a.a() == "ba"

    calculated_from.clear_cache(a, a.a)
    assert a.a() == "bb"

    a.c = "c"
    assert a.a() == "bb"

    calculated_from.clear_cache(a, "a")
    assert a.a() == "bc"
