#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_peng.py
#  
#  Copyright 2016 notna <notna@apparat.org>
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

import os
import pytest

import peng3d


def test_peng_create():
    p = peng3d.Peng()
    assert p.window is None
    assert isinstance(p, peng3d.peng.Peng) and isinstance(p, peng3d.Peng)
    assert peng3d.Peng is peng3d.peng.Peng


def test_peng_config():
    p = peng3d.Peng({"test.key1": "foo"})
    assert p.cfg["test.key1"] == "foo"


@pytest.mark.skip(reason="Dynamic skipif currently not working")
@pytest.mark.skipif(os.environ.get("DISPLAY", None) is None, reason="No Display available")
def test_peng_createwindow(peng):
    w = peng.createWindow()
    assert isinstance(w, peng3d.window.PengWindow)
    with pytest.raises(RuntimeError) as excinfo:
        peng.createWindow()
    assert excinfo.value.args[0] == "Window already created!"


def test_peng_eventhandling(peng):
    def test_handler(*args, **kwargs):
        assert kwargs == {}
        assert args == (1, 2, 3)
    peng.registerEventHandler("test_handler1", test_handler)
    peng.handleEvent("test_handler1", [1, 2, 3])
    # TODO: test that event actually arrives

# TODO: add run() test case
