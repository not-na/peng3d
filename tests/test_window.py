#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_window.py
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

import peng3d

import pytest

def test_window_eventHandling(window):
    def test_handler(*args,**kwargs):
        assert kwargs == {}
        assert args == (1,2,3)
    window.registerEventHandler("test_handler1",test_handler)
    window.handleEvent("test_handler1",[1,2,3])

def test_window_menu(window):
    with pytest.raises(KeyError) as excinfo:
        window.menu
    menu = peng3d.Menu("test",window,window.peng)
    window.addMenu(menu)
    assert window.activeMenu == None
    window.changeMenu("test")
    assert window.menu is menu

# TODO: add graphic tests
