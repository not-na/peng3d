#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_window_graphical.py
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


@pytest.mark.skip(reason="Internal Pyglet Tests")
@pytest.mark.graphical
def test_question_pass(event_loop):
    event_loop.create_window()
    event_loop.create_menu()
    event_loop.ask_question('If you read this text, you should let the test pass.')


@pytest.mark.skip(reason="Internal Pyglet Tests")
@pytest.mark.graphical
def test_question_fail(event_loop):
    event_loop.create_window()
    event_loop.create_menu()
    with pytest.raises(pytest.fail.Exception):
        event_loop.ask_question('Please press F to fail this test.')


@pytest.mark.skip(reason="Internal Pyglet Tests")
@pytest.mark.graphical
def test_question_skip(event_loop):
    event_loop.create_window()
    event_loop.create_menu()
    event_loop.ask_question('Please press S to skip the rest of this test.')
    pytest.fail('You should have pressed S')


@pytest.mark.skip(reason="Internal Pyglet Tests")
@pytest.mark.graphical
def test_window_exclusivity(event_loop):
    event_loop.create_window()
    event_loop.create_menu()
    event_loop.window.toggle_exclusivity()
    assert event_loop.window.exclusive == True
    event_loop.ask_question("Has your mouse been captured?")
    event_loop.window.toggle_exclusivity()
    assert event_loop.window.exclusive == False
    event_loop.ask_question("Has your mouse been released?")
