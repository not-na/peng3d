#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_config.py
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

import pytest

import peng3d

def test_config_defaults():
    cfg = peng3d.config.Config(defaults=peng3d.config.DEFAULT_CONFIG)
    for k,v in peng3d.config.DEFAULT_CONFIG.items():
        assert k not in cfg
        assert cfg[k]==v

def test_config_stacking():
    cfg1 = peng3d.config.Config(defaults={"key1":1})
    cfg2 = peng3d.config.Config(defaults=cfg1)
    
    assert cfg1["key1"]==1
    assert "key1" not in cfg1
    assert cfg2["key1"]==1
    assert "key1" not in cfg2
    
    cfg1["key1"]=2
    assert "key1" in cfg1
    assert cfg2["key1"]==2
    assert "key1" not in cfg2
    
    cfg2["key1"]=3
    assert cfg1["key1"]==2
    assert cfg2["key1"]==3
    assert "key1" in cfg2
    
    cfg2["key2"]="foo"
    with pytest.raises(KeyError):
        cfg1["key2"]
