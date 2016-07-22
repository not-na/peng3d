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

# Most of this code is from pyglet itself, with minor modifications to make it work with peng3d

import os

import pytest

import pyglet
from pyglet import clock
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.text.document import FormattedDocument
from pyglet.text.layout import TextLayout
from pyglet.window import Window, key
from pyglet.image import get_buffer_manager

import peng3d

#from .interactive import InteractiveFixture

local_dir = os.path.dirname(__file__)
test_dir = os.path.normpath(os.path.join(local_dir, '..'))

base_screenshot_path = os.path.join(test_dir, 'tests', 'screenshots')
committed_screenshot_path = os.path.join(base_screenshot_path, 'committed')
session_screenshot_path = os.path.join(base_screenshot_path, 'session')

@pytest.fixture
def event_loop(request,peng):
    return EventLoopFixture(request,peng)


class InteractiveFixture(object):
    """Fixture for interactive test cases. Provides interactive prompts and
    verifying screenshots.
    """
    def __init__(self, request):
        self.screenshots = []
        self._request = request

    @property
    def interactive(self):
        return not self.sanity and not self.non_interactive

    @property
    def sanity(self):
        return self._request.config.getoption('--sanity', False)

    @property
    def non_interactive(self):
        return self._request.config.getoption('--non-interactive', False)

    @property
    def allow_missing_screenshots(self):
        return not self.non_interactive

    @property
    def testname(self):
        parts = []
        parts.append(self._request.node.module.__name__)
        if self._request.node.cls:
            parts.append(self._request.node.cls.__name__)
        parts.append(self._request.node.name)
        return '.'.join(parts)

    def ask_question(self, description=None):
        """Ask a question to verify the current test result. Uses the console or an external gui
        as no window is available."""
        failure_description = None
        if self.interactive:
            failure_description = _ask_user_to_verify(description)
            if failure_description is not None:
                self.fail(failure_description)

    def _take_screenshot(self, window=None):
        """
        Take a screenshot to allow visual verification.
        """
        screenshot_name = self._get_next_screenshot_name()
        screenshot_file_name = self._get_screenshot_session_file_name(screenshot_name)

        if window is not None:
            window.switch_to()

        get_buffer_manager().get_color_buffer().image_data.save(screenshot_file_name)
        self.screenshots.append(screenshot_name)
        self._schedule_commit()

        return screenshot_name

    def _check_screenshot(self, screenshot_name):
        session_file_name = self._get_screenshot_session_file_name(screenshot_name)
        committed_file_name = self._get_screenshot_committed_file_name(screenshot_name)

        assert os.path.isfile(session_file_name)
        if os.path.isfile(committed_file_name):
            committed_image = pyglet.image.load(committed_file_name)
            session_image = pyglet.image.load(session_file_name)
            self.assert_image_equal(committed_image, session_image)
        else:
            assert self.allow_missing_screenshots
            warnings.warn('No committed reference screenshot available.')

    def _get_next_screenshot_name(self):
        """
        Get the unique name for the next screenshot.
        """
        return '{}.{:03d}.png'.format(self.testname,
                                      len(self.screenshots)+1)

    def _get_screenshot_session_file_name(self, screenshot_name):
        return os.path.join(session_screenshot_path, screenshot_name)

    def _get_screenshot_committed_file_name(self, screenshot_name):
        return os.path.join(committed_screenshot_path, screenshot_name)

    def _schedule_commit(self):
        if not hasattr(self._request.session, 'pending_screenshots'):
            self._request.session.pending_screenshots = set()
        self._request.session.pending_screenshots.add(self)

    def assert_image_equal(self, a, b, tolerance=0, msg=None):
        if msg is None:
            msg = 'Screenshot does not match last committed screenshot'
        if a is None:
            assert b is None, msg
        else:
            assert b is not None, msg

        a_data = a.image_data
        b_data = b.image_data

        assert a_data.width == b_data.width, msg
        assert a_data.height == b_data.height, msg
        assert a_data.format == b_data.format, msg
        assert a_data.pitch == b_data.pitch, msg
        self.assert_buffer_equal(a_data.data, b_data.data, tolerance, msg)

    def assert_buffer_equal(self, a, b, tolerance=0, msg=None):
        if tolerance == 0:
            assert a == b, msg

        assert len(a) == len(b), msg

        a = array.array('B', a)
        b = array.array('B', b)
        for (aa, bb) in zip(a, b):
            assert abs(aa - bb) <= tolerance, msg

    def commit_screenshots(self):
        """
        Store the screenshots for reference if the test case is successful.
        """
        for screenshot_name in self.screenshots:
            shutil.copyfile(self._get_screenshot_session_file_name(screenshot_name),
                            self._get_screenshot_committed_file_name(screenshot_name))

class EventLoopFixture(InteractiveFixture):

    question = '\n\n(P)ass/(F)ail/(S)kip/(Q)uit?'
    key_pass = key.P
    key_fail = key.F
    key_skip = key.S
    key_quit = key.Q
    clear_color = 1, 1, 1, 1
    base_options = {
            'width': 300,
            'height': 300,
            }

    def __init__(self, request, peng):
        super(EventLoopFixture, self).__init__(request)
        self._request = request
        self.window = None
        self.text_batch = None
        self.text_document = None
        self.answer = None
        self.peng = peng
        request.addfinalizer(self.tear_down)

    def tear_down(self):
        if self.window:
            self.window.close()
            self.window = None

    def create_window(self, **kwargs):
        combined_kwargs = {}
        combined_kwargs.update(self.base_options)
        combined_kwargs.update(kwargs)
        #self.window = Window(**combined_kwargs)
        self.window = self.peng.createWindow(**combined_kwargs)
        self.window.push_handlers(self)
        return self.window
    
    def create_menu(self,menu="menu"):
        m = TestMenu(self,menu,self.peng.window,self.peng)
        self.window.addMenu(m)
        self.window.changeMenu(menu)
        return m
    
    def get_document(self):
        if self.text_document is None:
            self._create_text()
        return self.text_document

    def _create_text(self):
        assert self.window is not None
        self.text_batch = Batch()
        self.text_document = FormattedDocument()
        layout = TextLayout(self.text_document, self.window.width, self.window.height,
                multiline=True, wrap_lines=True, batch=self.text_batch)
        layout.content_valign = 'bottom'

    def add_text(self, text):
        self.get_document()
        self.text_document.insert_text(len(self.text_document.text), text)
        self.window._legacy_invalid = True

    def ask_question(self, description=None, screenshot=True):
        """Ask a question inside the test window. By default takes a screenshot and validates
        that too."""
        if self.window is None:
            self.create_window()
        self.add_text('\n\n')
        if description:
            self.add_text(description)
        self.add_text(self.question)
        self.answer = None
        caught_exception = None
        try:
            if self.interactive:
                self.run_event_loop()
                self.handle_answer()
            else:
                self.run_event_loop(0.1)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            caught_exception = ex
        finally:
            if screenshot:
                try:
                    screenshot_name = self._take_screenshot(self.window)
                    if caught_exception is None and not self.interactive:
                        self._check_screenshot(screenshot_name)
                except:
                    if not caught_exception:
                        raise
            if caught_exception:
                raise caught_exception

    def handle_answer(self):
        if self.answer is None:
            raise Exception('Did not receive valid input in question window')
        elif self.answer == self.key_fail:
            # TODO: Ask input
            pytest.fail('Tester marked test failed')
        elif self.answer == self.key_skip:
            pytest.skip('Tester marked test skipped')
        elif self.answer == self.key_quit:
            pytest.exit('Tester requested to quit')

    def ask_question_no_window(self, description=None):
        """Ask a question to verify the current test result. Uses the console or an external gui
        as no window is available."""
        super(EventLoopFixture, self).ask_question(description)

    def run_event_loop(self, duration=None):
        if duration:
            clock.schedule_once(self.interrupt_event_loop, duration)
        pyglet.app.run()

    def interrupt_event_loop(self, *args, **kwargs):
        pyglet.app.exit()

    @staticmethod
    def schedule_once(callback, dt=.1):
        clock.schedule_once(callback, dt)

    def on_draw(self):
        self.clear()
        self.draw_text()

    def clear(self):
        gl.glClearColor(*self.clear_color)
        self.window.clear()

    def draw_text(self):
        if self.text_batch is not None:
            self.text_batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol in (self.key_pass, self.key_fail, self.key_skip, self.key_quit):
            self.answer = symbol
            self.interrupt_event_loop()

        # Prevent handling of Escape to close the window
        return True

class TestMenu(peng3d.menu.Menu):
    def __init__(self,event_loop,*args,**kwargs):
        super(TestMenu,self).__init__(*args,**kwargs)
        self.event_loop = event_loop
    def draw(self):
        super(TestMenu,self).draw()
        self.event_loop.draw_text()
