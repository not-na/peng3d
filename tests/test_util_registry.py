#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util_registry.py
#
#  Copyright 2017 notna <notna@apparat.org>
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

import pytest

import peng3d.util


def test_registry_empty():
    reg = peng3d.util.SmartRegistry(reuse_ids=False, start_id=0)

    assert reg.data["reg"] == {}

    assert reg.data["next_id"] == 0
    assert reg.genNewID() == 0

    reg["abc"] = None
    assert "abc" in reg
    assert 1 in reg


def test_registry_startid():
    reg = peng3d.util.SmartRegistry(reuse_ids=False, start_id=1000)

    assert reg.data["reg"] == {}

    assert reg.data["next_id"] == 1000

    assert reg.register("obj1") == 1000


def test_registry_autonextid():
    reg = peng3d.util.SmartRegistry(
        reuse_ids=False, start_id=100, default_reg={200: "obj2"}
    )

    # Covers force_id case
    assert reg.register("obj1", force_id=10) == 10

    assert reg.genNewID() == 201


def test_registry_reuseid():
    reg = peng3d.util.SmartRegistry(reuse_ids=True, start_id=100)

    assert reg.genNewID() == 100

    assert reg.register("abc") == 100

    assert reg.genNewID() == 101

    # Delete item and check if it re-assigned
    del reg["abc"]

    assert reg.genNewID() == 100
    assert reg.register("def") == 100
    assert reg.genNewID() == 101


def test_registry_maxid():
    reg = peng3d.util.SmartRegistry(reuse_ids=False, start_id=100, max_id=100)

    assert reg.data["reg"] == {}

    assert reg.register("obj1") == 100

    with pytest.raises(AssertionError):
        reg.register("obj2")


def test_registry_datatypes():
    with pytest.raises(TypeError) as exc_info:
        reg = peng3d.util.SmartRegistry(reuse_ids=False, default_reg="foo")
    assert "Default Registry must be a dictionary" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        reg = peng3d.util.SmartRegistry(reuse_ids=False, default_reg={"obj1": 10})
        # inverted
    assert "All keys must be integers" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        reg = peng3d.util.SmartRegistry(reuse_ids=False, default_reg={10: 10})
    assert "All values must be strings" in str(exc_info.value)


def test_registry_normalize_id():
    reg = peng3d.util.SmartRegistry(
        reuse_ids=False, default_reg={10: "obj1", 20: "obj2", 30: "obj3"}
    )

    with pytest.raises(AssertionError):
        reg.normalizeID(100)

    with pytest.raises(AssertionError):
        reg.normalizeID("obj_nonexistent")

    assert reg.normalizeID(10) == 10
    assert reg.normalizeID(20) == 20
    assert reg.normalizeID(30) == 30

    assert reg.normalizeID("obj1") == 10
    assert reg.normalizeID("obj2") == 20
    assert reg.normalizeID("obj3") == 30

    with pytest.raises(TypeError):
        reg.normalizeID(100.1)


def test_registry_normalize_name():
    reg = peng3d.util.SmartRegistry(
        reuse_ids=False, default_reg={10: "obj1", 20: "obj2", 30: "obj3"}
    )

    with pytest.raises(AssertionError):
        reg.normalizeName("obj_nonexistent")

    with pytest.raises(AssertionError):
        reg.normalizeName(100)

    assert reg.normalizeName("obj1") == "obj1"
    assert reg.normalizeName("obj2") == "obj2"
    assert reg.normalizeName("obj3") == "obj3"

    assert reg.normalizeName(10) == "obj1"
    assert reg.normalizeName(20) == "obj2"
    assert reg.normalizeName(30) == "obj3"

    assert reg["obj1"] == "obj1"
    assert reg[10] == "obj1"

    with pytest.raises(TypeError):
        reg.normalizeName(100.1)


def test_registry_contains():
    reg = peng3d.util.SmartRegistry(
        reuse_ids=False, default_reg={10: "obj1", 20: "obj2", 30: "obj3"}
    )

    assert 10 in reg
    assert 100 not in reg

    assert "obj1" in reg
    assert "obj100" not in reg


if __name__ == "__main__":
    test_registry_empty()
