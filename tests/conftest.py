#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  testfixtures.py
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

os.environ["DISPLAY"]=":0"
import pyglet
pyglet.options["shadow_window"]=False
import peng3d

#def pytest_runtest_setup():
#    for k,v in os.environ.items():print(k,v)
#    print("injecting...")
#    os.environ["DISPLAY"]=":0"
#    for k,v in os.environ.items():print(k,v)

def pytest_addoption(parser):
    parser.addoption("--x-display", action="store", default=":0",
        help="X Display to use")


@pytest.fixture(scope="module")
def xdisplay(request):
    return request.config.getoption("--x-display")

@pytest.fixture(scope="module")
def peng(request,xdisplay):
    os.environ["DISPLAY"]=xdisplay
    p = peng3d.Peng()
    def fin(p):
        def f():
            try:
                p.window.close()
            except Exception:
                print("pyglet window destroy Exception catched")
        return f
    request.addfinalizer(fin(p))
    return p

@pytest.fixture(scope="module")
def window(peng,xdisplay):
    os.environ["DISPLAY"]=xdisplay
    return peng.createWindow() if peng.window is None else peng.window

from graphicalhelpers import *
