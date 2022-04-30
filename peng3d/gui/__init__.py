#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

__all__ = ["GUIMenu", "SubMenu", "GUILayer", "FakeWidget"]

# from pprint import pprint
# import gc
# import weakref
# import sys
import collections

from typing import TYPE_CHECKING, Optional, Dict, List

if TYPE_CHECKING:
    import peng3d.window


try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass  # Headless mode

from ..menu import Menu
from ..layer import Layer, Layer2D
from .widgets import *
from .button import *
from .slider import *
from .text import *
from .container import *
from .layered import *
from .layout import *
from .. import util
from ..util.types import *


class FakeWidget(object):
    def __init__(self, parent):
        self.peng = parent.peng
        self.parent = parent
        self.submenu = parent

        self.pressed, self.is_hovering, self.enabled = False, False, True

    @property
    def pos(self):
        return [0, 0]  # As property to prevent bug with accidental manipulation

    @property
    def size(self):
        return self.parent.size


class GUIMenu(Menu):
    """
    :py:class:`peng3d.menu.Menu` subclass adding 2D GUI Support.

    Note that widgets are not managed directly by this class, but rather by each :py:class:`SubMenu`\\ .
    """

    def __init__(
        self,
        name: str,
        window: "peng3d.window.PengWindow",
        peng: "peng3d.Peng",
        font: str = "Arial",
        font_size: float = 16,
        font_color: Optional[ColorRGBA] = None,
        borderstyle: BorderStyle = "flat",
    ):
        super(GUIMenu, self).__init__(name, window, peng)
        pyglet.clock.schedule_interval(lambda dt: None, 1.0 / 30)
        self.submenus: Dict[str, "SubMenu"] = {}
        self.activeSubMenu: Optional[str] = None

        self.font: str = font
        self.font_size: float = font_size
        self.font_color: ColorRGBA = (
            font_color if font_color is not None else [62, 67, 73, 255]
        )
        self.borderstyle: BorderStyle = borderstyle

        self.batch2d: pyglet.graphics.Batch = pyglet.graphics.Batch()

        self.bg: BackgroundType = [242, 241, 240, 255]
        self.bg_vlist = pyglet.graphics.vertex_list(
            4,
            "v2f",
            "c4B",
        )

        # For compatibility with Background classes
        self.pressed: bool = False
        self.is_hovering: bool = False
        self.enabled: bool = True

        self.peng.keybinds.add(
            "enter", f"peng3d:menu.[{self.name}].send_form", self._on_send_form, False
        )

        self.peng.registerEventHandler("on_resize", self.on_resize)
        self.on_resize(*self.size)

    def addSubMenu(self, submenu: "SubMenu") -> None:
        """
        Adds a :py:class:`SubMenu` to this Menu.

        Note that nothing will be displayed unless a submenu is activated.
        """
        self.submenus[submenu.name] = submenu

    def changeSubMenu(self, submenu: str) -> None:
        """
        Changes the submenu that is displayed.

        :raises ValueError: if the name was not previously registered
        """
        if submenu not in self.submenus:
            raise ValueError("Submenu %s does not exist!" % submenu)
        elif submenu == self.activeSubMenu:
            return  # Ignore double submenu activation to prevent bugs in submenu initializer
        old = self.activeSubMenu
        self.activeSubMenu = submenu
        if old is not None:
            self.submenus[old].on_exit(submenu)
            self.submenus[old].doAction("exit")
        self.submenu.on_enter(old)
        self.submenu.doAction("enter")

    def draw(self) -> None:
        """
        Draws each menu layer and the active submenu.

        Note that the layers are drawn first and may be overridden by the submenu and widgets.
        """
        super(GUIMenu, self).draw()
        # TODO: find a way to re-raise these exceptions bypassing pyglet
        try:
            self.submenu.draw()
        except (AttributeError, TypeError):
            import traceback

            traceback.print_exc()

    def draw_bg(self) -> None:
        # Draws the background
        if isinstance(self.bg, Layer):
            self.bg._draw()
        elif hasattr(self.bg, "draw") and callable(self.bg.draw):
            self.bg.draw()
        elif isinstance(self.bg, list) or isinstance(self.bg, tuple):
            self.bg_vlist.draw(GL_QUADS)
        elif callable(self.bg):
            self.bg()
        elif isinstance(self.bg, Background):
            # The background will be drawn via the batch
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.redraw_bg()
                self.bg.initialized = True
        elif self.bg == "blank":
            pass
        elif self.bg is None:
            raise RuntimeError("Cannot set Menu background to None")
        else:
            raise TypeError("Unknown/Unsupported background type")

        self.batch2d.draw()

    def setBackground(self, bg: BackgroundType):
        self.bg = bg
        if isinstance(bg, list) or isinstance(bg, tuple):
            if len(bg) == 3 and isinstance(bg, list):
                bg.append(255)
            self.bg_vlist.colors = bg * 4
        elif bg in ["flat", "gradient", "oldshadow", "material"]:
            self.bg = ContainerButtonBackground(self, borderstyle=bg)
            self.on_resize(self.window.width, self.window.height)

    @property
    def submenu(self) -> "SubMenu":
        """
        Property containing the :py:class:`SubMenu` instance that is currently active.
        """
        return self.submenus[self.activeSubMenu]

    # The following properties are needed for compatibility with Background classes
    @property
    def pos(self) -> List[int]:
        return [0, 0]  # As property to prevent bug with accidental manipulation

    @property
    def size(self) -> List[int]:
        return self.window.get_size()

    def on_resize(self, width, height):
        sx, sy = width, height
        self.bg_vlist.vertices = [0, 0, sx, 0, sx, sy, 0, sy]
        if isinstance(self.bg, Background):
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.initialized = True
            self.bg.redraw_bg()

    def on_enter(self, old):
        super().on_enter(old)

        self.submenu.redraw()

    def _on_send_form(self, symbol, modifiers, release):
        # TODO: support context here
        if release:
            return
        self.submenu.send_form()


class SubMenu(util.ActionDispatcher):
    """
    Sub Menu of the GUI system.

    Each instance must be registered with their menu to work properly, see :py:meth:`GUIMenu.addSubMenu()`\\ .

    Actions supported by default:

    ``enter`` is triggered everytime the :py:meth:`on_enter()` method has been called.

    ``exit`` is triggered everytime the :py:meth:`on_exit()` method has been called.

    ``send_form`` is triggered if the contained form is sent by either pressing enter or
    calling :py:meth:`send_form()`\\ .
    """

    def __init__(
        self,
        name: str,
        menu: GUIMenu,
        window: "peng3d.window.PengWindow",
        peng: "peng3d.Peng",
        font: Optional[str] = None,
        font_size: Optional[float] = None,
        font_color: Optional[ColorRGBA] = None,
        borderstyle: Optional[BorderStyle] = None,
    ):
        self.name: str = name
        self.menu: GUIMenu = menu
        self.window: "peng3d.window.PengWindow" = window
        self.peng: "peng3d.Peng" = peng

        self.font: str = font if font is not None else self.menu.font
        self.font_size: float = (
            font_size if font_size is not None else self.menu.font_size
        )
        self.font_color: ColorRGBA = (
            font_color if font_color is not None else self.menu.font_color
        )
        self.borderstyle: BorderStyle = (
            borderstyle if borderstyle is not None else self.menu.borderstyle
        )

        self.widgets = collections.OrderedDict()

        self.widget_order = {}

        self.bg: BackgroundType = None
        self.bg_vlist = pyglet.graphics.vertex_list(
            4,
            "v2f",
            "c4B",
        )
        self.peng.registerEventHandler("on_resize", self.on_resize)
        self.on_resize(*self.size)

        self.batch2d: pyglet.graphics.Batch = pyglet.graphics.Batch()

        self.form_ctx = None

        # For compatibility with Background classes
        self.pressed: bool = False
        self.is_hovering: bool = False

    def draw(self) -> None:
        """
        Draws the submenu and its background.

        Note that this leaves the OpenGL state set to 2d drawing.
        """
        # Sets the OpenGL state for 2D-Drawing
        self.window.set2d()

        # Draws the background
        if isinstance(self.bg, Layer):
            self.bg._draw()
        elif hasattr(self.bg, "draw") and callable(self.bg.draw):
            self.bg.draw()
        elif isinstance(self.bg, list) or isinstance(self.bg, tuple):
            self.bg_vlist.draw(GL_QUADS)
        elif callable(self.bg):
            self.bg()
        elif isinstance(self.bg, Background):
            # The background will be drawn via the batch
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.redraw_bg()
                self.bg.initialized = True
        elif self.bg == "blank":
            pass
        elif self.bg is None:
            self.menu.draw_bg()
        else:
            raise TypeError("Unknown/Unsupported background type")

        # In case the background modified relevant state
        self.window.set2d()

        # Check that all widgets that need redrawing have been redrawn
        for widget in self.widgets.values():
            if widget.do_redraw:
                widget.on_redraw()
                widget.do_redraw = False

        # Actually draw the content
        self.batch2d.draw()

        # Call custom draw methods where needed
        # for widget in self.widgets.values():
        #    widget.draw()
        for order in sorted(self.widget_order.keys()):
            for w in self.widget_order[order]:
                w.draw()

    def addWidget(self, widget: BasicWidget, order_key: int = 0) -> None:
        """
        Adds a widget to this submenu.

        ``order_key`` optionally specifies the "layer" this widget will be on. Note that
        this does not work with batched widgets. All batched widgets will be drawn before
        widgets that use a custom draw() method.

        .. deprecated:: 1.12.0
            This method is no longer needed in most cases, since widgets now register themselves by default.
        """
        if widget.name in self.widgets:
            # Just ignore duplicated registrations, since existing code will cause a lot of these
            return

        self.widgets[widget.name] = widget

        if order_key not in self.widget_order:
            self.widget_order[order_key] = []
        self.widget_order[order_key].append(widget)

    def getWidget(self, name: str) -> BasicWidget:
        """
        Returns the widget with the given name.
        """
        return self.widgets[name]

    def delWidget(self, widget: str) -> None:
        """
        Deletes the widget by the given name.

        Note that this feature is currently experimental as there seems to be a memory leak with this method.
        """
        # TODO: fix memory leak upon widget deletion
        # print("*"*50)
        # print("Start delWidget")
        if isinstance(widget, BasicWidget):
            widget = widget.name

        if widget not in self.widgets:
            return

        w = self.widgets[widget]

        # print("refs: %s"%sys.getrefcount(w))

        w.delete()
        del self.widgets[widget]
        del widget

        for o in self.widget_order:
            if w in o:
                del o[o.index(w)]

        # w_wref = weakref.ref(w)

        # print("GC: GARBAGE")
        # print(gc.garbage)
        # print("Widget Info")
        # print(w_wref())
        # import objgraph
        # print("Objgraph")
        # objgraph.show_refs([w], filename='./mem_widget.png')
        # print("refs: %s"%sys.getrefcount(w))
        # w_r = gc.get_referrers(w)
        # print("GC: REFS")
        # for w_ref in w_r:
        #    print(repr(w_ref)[:512])
        # print("GC: END")
        # print("len: %s"%len(w_r))
        # del w_ref,w_r
        # print("after del %s"%w_wref())
        # print("refs: %s"%sys.getrefcount(w))
        del w
        # print("Final WRef")
        # print(w_wref())

    def setBackground(self, bg: BackgroundType) -> None:
        """
        Sets the background of the submenu.

        The background may be a RGB or RGBA color to fill the background with.

        Alternatively, a :py:class:`peng3d.layer.Layer` instance or other object with a ``.draw()`` method may be supplied.
        It is also possible to supply any other method or function that will get called.

        Also, the strings ``flat``\\ , ``gradient``\\ , ``oldshadow`` and ``material`` may be given, resulting in a background that looks similar to buttons.

        If the Background is ``None``\\ , the default background of the parent menu will be used.

        Lastly, the string ``"blank"`` may be passed to skip background drawing.
        """
        self.bg = bg
        if isinstance(bg, list) or isinstance(bg, tuple):
            if len(bg) == 3 and isinstance(bg, list):
                bg.append(255)
            self.bg_vlist.colors = bg * 4
        elif bg in ["flat", "gradient", "oldshadow", "material"]:
            self.bg = ContainerButtonBackground(self, borderstyle=bg)
            self.on_resize(self.window.width, self.window.height)

    def redraw(self) -> None:
        for widget in self.widgets.values():
            widget.on_mouse_motion(*self.window.mouse_pos, 0, 0)
            widget.redraw()

    # The following properties are needed for compatibility with Background classes
    @property
    def pos(self) -> List[int]:
        return [0, 0]  # As property to prevent bug with accidental manipulation

    @property
    def size(self) -> List[int]:
        return self.window.get_size()

    @property
    def submenu(self) -> "SubMenu":
        return self

    @property
    def enabled(self) -> bool:
        return self.menu.submenu is self and self.window.menu is self.menu

    def send_form(self, ctx=None) -> bool:
        """
        Triggers whatever form data is entered to be sent.

        Only causes action ``send_form`` to be sent if submenu is active and :py:meth:`form_valid()`
        returns true.

        The given context is stored in :py:attr:`form_ctx`\\ .

        :param ctx: Arbitrary context
        :return: If the form was actually sent
        """
        if self.enabled and self.form_valid(ctx):
            self.form_ctx = ctx
            self.doAction("send_form")
            return True
        return False

    def form_valid(self, ctx=None) -> bool:
        """
        Called to pre-check if a form is valid.

        Should be overridden by subclasses.

        By default, this always returns true.

        :param ctx: Arbitrary context
        :return: If the form is valid
        """
        return True

    def on_resize(self, width, height):
        sx, sy = width, height
        self.bg_vlist.vertices = [0, 0, sx, 0, sx, sy, 0, sy]
        if isinstance(self.bg, Background):
            if not self.bg.initialized:
                self.bg.init_bg()
                self.bg.initialized = True
            self.bg.redraw_bg()

    def on_enter(self, old):
        pass

    def on_exit(self, new):
        pass


class GUILayer(GUIMenu, Layer2D):
    """
    Hybrid of :py:class:`GUIMenu` and :py:class:`peng3d.layer.Layer2D`\\ .

    This class allows you to create Head-Up Displays and other overlays easily.
    """

    # TODO: add safety recursion breaker if this is added as a layer to itself
    def __init__(
        self,
        name: str,
        menu: Menu,
        window: "peng3d.window.PengWindow",
        peng: "peng3d.Peng",
    ):
        Layer2D.__init__(self, menu, window, peng)
        GUIMenu.__init__(self, menu.name, window, peng)

    def draw(self) -> None:
        """
        Draws the Menu.
        """
        self.predraw()
        GUIMenu.draw(self)
        self.postdraw()


# Hack to allow Container to use the drawing method of SubMenu for itself
from ..gui import container

container.SubMenu = SubMenu

# To allow menus to subclass SubMenu
from .menus import *
