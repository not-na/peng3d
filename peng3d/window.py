#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  window.py
#
#  Copyright 2016-2022 notna <notna@apparat.org>
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

__all__ = ["PengWindow"]

import math
import time
import traceback
import weakref
import inspect

import pyglet
from pyglet.gl import *
from pyglet.window import key

from . import config, camera
from .util.gui import Position

from typing import TYPE_CHECKING, Dict, Optional, Union, Tuple

if TYPE_CHECKING:
    import peng3d

# TODO: allow for arbitrary icon size discovery
ICON_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]


class PengWindow(pyglet.window.Window):
    """
    Main window class for peng3d and subclass of :py:class:`pyglet.window.Window()`\\ .

    This class should not be instantiated directly, use the :py:meth:`Peng.createWindow()` method.
    """

    def __init__(self, peng: "peng3d.Peng", *args, **kwargs):
        if peng.cfg["graphics.stencil.enable"]:
            glconfig = pyglet.gl.Config(stencil_size=peng.cfg["graphics.stencil.bits"])
            kwargs["config"] = glconfig
        super(PengWindow, self).__init__(*args, **kwargs)
        self.peng: "peng3d.Peng" = peng

        self.exclusive: bool = False
        self.started: bool = False

        self.menus: Dict[str, "peng3d.BasicMenu"] = {}
        self.activeMenu: Optional[str] = None

        self.cfg: config.Config = config.Config({}, defaults=peng.cfg)
        self.eventHandlers = {}

        self.cur_fps: Optional[float] = None
        self._last_render = time.monotonic()

        self._setup = False

        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                return pyglet.event.EVENT_HANDLED

        self.push_handlers(on_key_press)  # to stop the auto-exit on escape

        self.mouse_pos: Position = [0, 0]

        self.peng.sendEvent("peng3d:window.create", {"peng": self.peng, "window": self})

    def setup(self):
        """
        Sets up the OpenGL state.

        This method should be called once after the config has been created and before the main loop is started.
        You should not need to manually call this method, as it is automatically called by :py:meth:`run()`\\ .

        Repeatedly calling this method has no effects.
        """
        if self._setup:
            return
        self._setup = True

        # Ensures that default values are supplied
        # self.cleanConfig()

        # Sets min/max window size, if specified
        if self.cfg["graphics.min_size"] is not None:
            self.set_minimum_size(*self.cfg["graphics.min_size"])
        if self.cfg["graphics.max_size"] is not None:
            self.set_maximum_size(*self.cfg["graphics.max_size"])

        # Sets up basic OpenGL state
        glClearColor(*self.cfg["graphics.clearColor"])

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

        glShadeModel(GL_SMOOTH)

        if self.cfg["graphics.fogSettings"]["enable"]:
            self.setupFog()
        if self.cfg["graphics.lightSettings"]["enable"]:
            self.setupLight()

    def setupFog(self):
        """
        Sets the fog system up.

        The specific options available are documented under :confval:`graphics.fogSettings`\\ .
        """
        fogcfg = self.cfg["graphics.fogSettings"]
        if not fogcfg["enable"]:
            return

        glEnable(GL_FOG)

        if fogcfg["color"] is None:
            fogcfg["color"] = self.cfg["graphics.clearColor"]
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*fogcfg["color"]))
        # Set the performance hint.
        glHint(
            GL_FOG_HINT, GL_DONT_CARE
        )  # TODO: add customization, including headless support
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, fogcfg["start"])
        glFogf(GL_FOG_END, fogcfg["end"])

    def setupLight(self):
        """
        Sets the light system up.

        The specific options available are documented under :confval:`graphics.lightSettings`\\ .

        Note that this feature is currently not implemented.
        """
        raise NotImplementedError("Currently not implemented")

    def run(self, evloop: Optional["pyglet.app.EventLoop"] = None) -> None:
        """
        Runs the application in the current thread.

        This method should not be called directly, especially when using multiple windows, use :py:meth:`Peng.run()` instead.

        Note that this method is blocking as rendering needs to happen in the main thread.
        It is thus recommendable to run your game logic in another thread that should be started before calling this method.

        ``evloop`` may optionally be a subclass of :py:class:`pyglet.app.base.EventLoop` to replace the default event loop.
        """
        self.setup()
        self.cur_fps = self.cfg["graphics.default_fps"]

        if evloop is not None:
            pyglet.app.event_loop = evloop

        pyglet.app.run()  # This currently just calls the basic pyglet main loop, maybe implement custom main loop for more control

    # Various methods
    def changeMenu(self, menu: str) -> None:
        """
        Changes to the given menu.

        ``menu`` must be a valid menu name that is currently known.
        """
        if menu not in self.menus:
            raise ValueError("Menu %s does not exist!" % menu)
        elif menu == self.activeMenu:
            return  # Ignore double menu activation to prevent bugs in menu initializer

        old = self.activeMenu
        self.activeMenu = menu

        if old is not None:
            self.menus[old].on_exit(menu)
            self.menus[old].doAction("exit")

        self.menu.on_enter(old)
        self.menu.doAction("enter")
        self.peng.sendEvent(
            "peng3d:window.menu.change",
            {"peng": self.peng, "window": self, "old": old, "menu": menu},
        )

    def addMenu(self, menu: "peng3d.BasicMenu") -> "peng3d.BasicMenu":
        """
        Adds a menu to the list of menus.
        """
        # If there is no menu selected currently, this menu will automatically be made active.
        # Add the line above to the docstring if fixed
        self.menus[menu.name] = menu
        self.peng.sendEvent(
            "peng3d:window.menu.add", {"peng": self.peng, "window": self, "menu": menu}
        )
        # if self.activeMenu is None:
        #    self.changeMenu(menu.name)
        # currently disabled because of a bug with adding layers

        return menu

    def setIcons(self, icons: Union[str, tuple]):
        if isinstance(icons, list) or isinstance(icons, tuple):
            # should be a list of resource names
            rlist = icons
        else:
            # We were given a string, need to expand it first
            rlist = []
            for isize in ICON_SIZES:
                rname = icons.format(size=isize)
                if self.peng.rsrcMgr.resourceExists(rname, ".png"):
                    # Resource exists, add it to list
                    rlist.append(rname)

        ilist = []
        for rname in rlist:
            ilist.append(
                pyglet.image.load(self.peng.rsrcMgr.resourceNameToPath(rname, ".png"))
            )

        if len(ilist) != 0:
            self.set_icon(*ilist)

    def set_fps(self, fps: Optional[float]):
        """
        Sets the new FPS limit.

        This limit will be used until the application closes or this method is called again.

        A value of ``None`` will cause the FPS limit to be disabled.

        Note that this is only a limit, which may or may not be fulfilled depending on available
        resources.

        .. note::
           By default, pyglet only redraws the window when an event arrives. To force a certain
           redraw rate (which still respects system performance), call :py:meth:`pyglet.clock.schedule_interval()`
           once during initialization with a dummy function and your desired refresh rate in seconds.

        :param fps:
        :return:
        """
        self.cur_fps = fps

    # Event handlers
    def on_draw(self):
        """
        Clears the screen and draws the currently active menu.
        """
        if (
            self.cur_fps is not None
            and self._last_render + (1 / self.cur_fps) > time.monotonic()
        ):
            self.invalid = False
            return
        self._last_render = time.monotonic()
        self.peng._pumpRateLimitedEvents()
        self.clear()

        if self.activeMenu in self.menus:
            self.menu.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = x, y

    def dispatch_event(self, event_type: str, *args):
        """
        Internal event handling method.

        This method extends the behavior inherited from :py:meth:`pyglet.window.Window.dispatch_event()` by calling the various :py:meth:`handleEvent()` methods.

        By default, :py:meth:`Peng.handleEvent()`\\ , :py:meth:`handleEvent()` and :py:meth:`Menu.handleEvent()` are called in this order to handle events.

        Note that some events may not be handled by all handlers during early startup.
        """
        super(PengWindow, self).dispatch_event(event_type, *args)
        try:
            p = self.peng
            m = self.menu
        except AttributeError:
            # To prevent early startup errors
            if hasattr(self, "peng") and self.peng.cfg["debug.events.logerr"]:
                print("Error:")
                traceback.print_exc()
            return
        p.handleEvent(event_type, args, self)
        self.handleEvent(event_type, args)
        m.handleEvent(event_type, args)

    def handleEvent(self, event_type: str, args: Tuple, window=None):
        args = list(args)
        # if window is not None:
        #    args.append(window)
        if event_type in self.eventHandlers:
            for whandler in self.eventHandlers[event_type]:
                # This allows for proper collection of deleted handler methods by using weak references
                handler = whandler()
                if handler is None:
                    del self.eventHandlers[event_type][
                        self.eventHandlers[event_type].index(whandler)
                    ]
                handler(*args)

    handleEvent.__noautodoc__ = True

    def registerEventHandler(self, event_type, handler):
        if self.peng.cfg["debug.events.register"]:
            print("Registered Event: %s Handler: %s" % (event_type, handler))
        if event_type not in self.eventHandlers:
            self.eventHandlers[event_type] = []
        # Only a weak reference is kept
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        else:
            handler = weakref.ref(handler)
        self.eventHandlers[event_type].append(handler)

    # Properties/Proxies for various things

    # Proxy for self.menus[self.activeMenu]
    @property
    def menu(self) -> "peng3d.BasicMenu":
        """
        Property for accessing the currently active menu.

        Always equals ``self.menus[self.activeMenu]``\\ .

        This property is read-only.
        """
        return self.menus[self.activeMenu]

    # Utility methods

    def toggle_exclusivity(self, override=None):
        """
        Toggles mouse exclusivity via pyglet's :py:meth:`set_exclusive_mouse()` method.

        If ``override`` is given, it will be used instead.

        You may also read the current exclusivity state via :py:attr:`exclusive`\\ .
        """
        if override is not None:
            new = override
        else:
            new = not self.exclusive
        self.exclusive = new
        self.set_exclusive_mouse(self.exclusive)
        self.peng.sendEvent(
            "peng3d:window.toggle_exclusive",
            {"peng": self.peng, "window": self, "exclusive": self.exclusive},
        )

    def set2d(self):
        """
        Configures OpenGL to draw in 2D.

        Note that wireframe mode is always disabled in 2D-Mode, but can be re-enabled by calling ``glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)``\\ .
        """
        # Light

        glDisable(GL_LIGHTING)

        # To avoid accidental wireframe GUIs and fonts
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set3d(self, cam):
        """
        Configures OpenGL to draw in 3D.

        This method also applies the correct rotation and translation as set in the supplied camera ``cam``\\ .
        It is discouraged to use :py:func:`glTranslatef()` or :py:func:`glRotatef()` directly as this may cause visual glitches.

        If you need to configure any of the standard parameters, see the docs about :doc:`/configoption`\\ .

        The :confval:`graphics.wireframe` config value can be used to enable a wireframe mode, useful for debugging visual glitches.
        """
        if not isinstance(cam, camera.Camera):
            raise TypeError("cam is not of type Camera!")

        # Light

        # glEnable(GL_LIGHTING)

        if self.cfg["graphics.wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            self.cfg["graphics.fieldofview"],
            width / float(height),
            self.cfg["graphics.nearclip"],
            self.cfg["graphics.farclip"],
        )  # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = cam.rot
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = cam.pos
        glTranslatef(-x, -y, -z)
