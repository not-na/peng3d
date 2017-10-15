#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util_action.py
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

def make_fake_handler(name):
    dispatch_log = []
    def fake_action_handler(*args,**kwargs):
        dispatch_log.append([name,args,kwargs])
    return dispatch_log,fake_action_handler

def add_fake_handler(name,dispatch_log):
    def fake_action_handler(*args,**kwargs):
        dispatch_log.append([name,args,kwargs])
    return fake_action_handler

def _norm_handler(handler):
    if len(handler)==1:
        name = handler[0]
        args,kwargs = (),{}
    elif len(handler)==2:
        name,args = handler
        kwargs = {}
    elif len(handler)==3:
        name,args,kwargs = handler
    else:
        pytest.fail("invalid configuration, handler must be of length 1,2,3 not %s"%len(handler))
    return name,args,kwargs

def make_fake_handler_multi(names,dispatcher):
    name,args,kwargs = _norm_handler(names[0])
    dispatch_log,func = make_fake_handler(name)
    dispatcher.addAction(name,func,*args,**kwargs)
    del names[0]
    
    for handler in names:
        name,args,kwargs = _norm_handler(handler)
        dispatcher.addAction(name,add_fake_handler(name,dispatch_log),*args,**kwargs)
    
    return dispatch_log

def test_action_testutils(dispatcher):
    assert not hasattr(dispatcher,"actions")
    
    dispatch_log,handler = make_fake_handler("test_action_testutils")
    
    dispatcher.addAction("test_action_testutils",handler)
    
    # test if args are treated correctly is done in test_action_noargs
    assert hasattr(dispatcher,"actions")
    assert "test_action_testutils" in dispatcher.actions
    assert (handler,(),{}) in dispatcher.actions["test_action_testutils"]

def test_action_misfire(dispatcher):
    dispatch_log,handler = make_fake_handler("test_action_misfire")
    
    dispatcher.addAction("test_action_misfire",handler)
    
    assert hasattr(dispatcher,"actions")
    assert "test_action_misfire" in dispatcher.actions
    assert (handler,(),{}) in dispatcher.actions["test_action_misfire"]
    
    assert dispatch_log == []
    
    dispatcher.doAction("test_nonexistent") # completely different
    assert dispatch_log == []
    
    dispatcher.doAction("TEST_ACTION_MISFIRE") # all caps, but same letters
    assert dispatch_log == []

def test_action_noargs(dispatcher):
    test_actions = [
        ["test_action_noargs"],
        ]
    dispatch_log = make_fake_handler_multi(test_actions,dispatcher)
    
    assert dispatch_log == []
    
    dispatcher.doAction("test_action_noargs")
    
    assert dispatch_log == [["test_action_noargs",(),{}]]

def test_action_posargs(dispatcher):
    test_actions = [
        ["test_action_posargs",["some","argument",1,3.14,True]],
        ]
    dispatch_log = make_fake_handler_multi(test_actions,dispatcher)
    
    assert dispatch_log == []
    
    dispatcher.doAction("test_action_posargs")
    
    assert dispatch_log == [["test_action_posargs",("some","argument",1,3.14,True),{}]]

def test_action_kwargs(dispatcher):
    test_actions = [
        ["test_action_kwargs",[],{"key":"value","kwarg":2}],
        ]
    dispatch_log = make_fake_handler_multi(test_actions,dispatcher)
    
    assert dispatch_log == []
    
    dispatcher.doAction("test_action_kwargs")
    
    assert dispatch_log == [["test_action_kwargs",(),{"key":"value","kwarg":2}]]

def test_action_combargs(dispatcher):
    test_actions = [
        ["test_action_combargs",["some","argument",1,3.14,True],{"key":"value","kwarg":2}],
        ]
    dispatch_log = make_fake_handler_multi(test_actions,dispatcher)
    
    assert dispatch_log == []
    
    dispatcher.doAction("test_action_combargs")
    
    assert dispatch_log == [["test_action_combargs",("some","argument",1,3.14,True),{"key":"value","kwarg":2}]]
