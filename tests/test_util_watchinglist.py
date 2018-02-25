#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util_watchinglist.py
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

import peng3d

@pytest.fixture
def wl():
    return peng3d.util.WatchingList([0,"foo",True,1])

def test_length(wl):
    # Length check
    assert len(wl)==4

def test_index_read(wl):
    # Basic indexing
    assert wl[0]==0
    assert wl[1]=="foo"
    assert wl[2]==True
    assert wl[3]==1

def test_index_write(wl):
    # Indexed write
    assert wl[0]==0
    wl[0]=1
    assert wl[0]==1
    
    assert wl[1]=="foo"
    wl[1]=False
    assert wl[1]==False

def test_index_advanced_read(wl):
    # Advanced indexing
    assert wl[-1]==1
    assert wl[-2]==True

def test_index_advanced_write(wl):
    # Advanced writing
    assert wl[-1]==1
    wl[-1]="bar"
    assert wl[-1]=="bar"

def test_slicing_read(wl):
    # Slicing
    # TODO
    pass

def test_slicing_write(wl):
    # Sliced write
    # TODO
    pass

# TODO: add tests for callback methods/lambdas/functions
