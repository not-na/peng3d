#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  peng.py
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

__all__ = ["Peng","HeadlessPeng"]

import sys

import weakref
import inspect

#from . import window, config, keybind, pyglet_patch
from . import config, world, resource, i18n

_pyglet_patched = sys.version_info.major == 2 or not world._have_pyglet

class Peng(object):
    """
    This Class should only be instantiated once per application, if you want to use multiple windows, see :py:meth:`createWindow()`\\ .
    
    An Instance of this class represents the whole Engine, with all accompanying state and window/world objects.
    
    Be sure to keep your instance accessible, as it will be needed to create most other classes.
    """
    
    def __init__(self,cfg={}):
        global _pyglet_patched
        if world._have_pyglet:
            from . import pyglet_patch, keybind # Local import for compat with headless machines
        self.window = None
        
        self.pygletEventHandlers = {}
        self.rlPygletEventHandlers = {}
        self.rlPygletEventHandlersParams = {
            "on_mouse_motion": (0, 0, 0, 0),
            "on_resize": (0, 0),
        }
        self.rlPygletEventHandlersTriggered = {
            "on_mouse_motion": False,
            "on_resize": False,
        }
        
        self.eventHandlers = {}
        
        self.events_ignored = {}
        self.event_list = set()
        
        if cfg == {}:
            cfg = {} # To avoid bugs with default arguments
        self.cfg = config.Config(cfg,defaults=config.DEFAULT_CONFIG)
        if world._have_pyglet:
            self.keybinds = keybind.KeybindHandler(self)
        
        self.resourceMgr = None
        self.i18n = None
        
        self.t = lambda *args,**kwargs:self._t(*args,**kwargs)
        self.tl = lambda *args,**kwargs:self._tl(*args,**kwargs)
        
        self.addEventListener("peng3d:peng.exit",self.handler_exit)
        self.registerEventHandler("on_mouse_motion", self.on_mouse_motion)
        self.registerEventHandler("on_resize", self.on_resize)
        
        if not _pyglet_patched and self.cfg["pyglet.patch.patch_float2int"]:
            _pyglet_patched = True
            pyglet_patch.patch_float2int()
    
    def createWindow(self,cls=None,caption_t=None,rsrc_class=resource.ResourceManager, *args,**kwargs):
        """
        createWindow(cls=window.PengWindow, *args, **kwargs)
        
        Creates a new window using the supplied ``cls``\\ .
        
        If ``cls`` is not given, :py:class:`peng3d.window.PengWindow()` will be used.
        
        Any other positional or keyword arguments are passed to the class constructor.
        
        Note that this method currently does not support using multiple windows.
        
        .. todo::
           
           Implement having multiple windows.
        """
        if cls is None:
            from . import window
            cls = window.PengWindow
        if self.window is not None:
            raise RuntimeError("Window already created!")
        self.sendEvent("peng3d:window.create.pre",{"peng":self,"cls":cls})
        if caption_t is not None:
            kwargs["caption"] = "Peng3d Application"
        self.window = cls(self,*args,**kwargs)
        self.sendEvent("peng3d:window.create.post",{"peng":self,"window":self.window})
        if self.cfg["rsrc.enable"] and self.resourceMgr is None:
            self.sendEvent("peng3d:rsrc.init.pre",{"peng":self,"basepath":self.cfg["rsrc.basepath"]})
            self.resourceMgr = rsrc_class(self,self.cfg["rsrc.basepath"])
            self.rsrcMgr = self.resourceMgr
            self.sendEvent("peng3d:rsrc.init.post",{"peng":self,"rsrcMgr":self.resourceMgr})
        if self.resourceMgr is not None and self.cfg["i18n.enable"] and self.i18n is None:
            self.sendEvent("peng3d:i18n.init.pre",{"peng":self})
            self.i18n = i18n.TranslationManager(self)
            self._t = self.i18n.t
            self._tl = self.i18n.tl
            self.sendEvent("peng3d:i18n.init.post",{"peng":self,"i18n":self.i18n})
            if caption_t is not None:
                self.window.set_caption(self.t(caption_t))
                def f():
                    self.window.set_caption(self.t(caption_t))
                self.i18n.addAction("setlang",f)
                return self.window
        if caption_t is not None:
            raise RuntimeError("Could not set translated window title since either the resource system or i18n has been disabled")
        return self.window
    
    def run(self,evloop=None):
        """
        Runs the application main loop.
        
        This method is blocking and needs to be called from the main thread to avoid OpenGL bugs that can occur.
        
        ``evloop`` may optionally be a subclass of :py:class:`pyglet.app.base.EventLoop` to replace the default event loop.
        """
        # TODO: support more than one event loop
        self.sendEvent("peng3d:peng.run",{"peng":self,"window":self.window,"evloop":evloop})
        self.window.run(evloop)
        self.sendEvent("peng3d:peng.exit",{"peng":self})
    
    def sendPygletEvent(self,event_type,args,window=None):
        """
        Handles a pyglet event.
        
        This method is called by :py:meth:`PengWindow.dispatch_event()` and handles all events.
        
        See :py:meth:`registerEventHandler()` for how to listen to these events.
        
        This method should be used to send pyglet events.
        For new code, it is recommended to use :py:meth:`sendEvent()` instead.
        For "tunneling" pyglet events, use event names of the format ``pyglet:<event>``
        and for the data use ``{"args":<args as list>,"window":<window object or none>,"src":<event source>,"event_type":<event type>}``
        
        Note that you should send pyglet events only via this method, the above event will be sent automatically.
        
        Do not use this method to send custom events, use :py:meth:`sendEvent` instead.
        """
        args = list(args)
        
        self.sendEvent("pyglet:%s"%event_type,{"peng":self,"args":args,"window":window,"src":self,"event_type":event_type})
        self.sendEvent("peng3d:pyglet",{"peng":self,"args":args,"window":window,"src":self,"event_type":event_type})
        
        if event_type not in ["on_draw","on_mouse_motion"] and self.cfg["debug.events.dump"]:
            print("Event %s with args %s"%(event_type,args))
        if event_type in self.pygletEventHandlers:
            for whandler in self.pygletEventHandlers[event_type]:
                # This allows for proper collection of deleted handler methods by using weak references
                handler = whandler()
                if handler is None:
                    del self.pygletEventHandlers[event_type][self.pygletEventHandlers[event_type].index(whandler)]
                handler(*args)
    def addPygletListener(self,event_type,handler):
        """
        Registers an event handler.
        
        The specified callable handler will be called every time an event with the same ``event_type`` is encountered.
        
        All event arguments are passed as positional arguments.
        
        This method should be used to listen for pyglet events.
        For new code, it is recommended to use :py:meth:`addEventListener()` instead.
        
        See :py:meth:`handleEvent()` for information about tunneled pyglet events.
        
        For custom events, use :py:meth:`addEventListener()` instead.
        """
        if self.cfg["debug.events.register"]:
            print("Registered Event: %s Handler: %s"%(event_type,handler))
        if event_type not in self.pygletEventHandlers:
            self.pygletEventHandlers[event_type]=[]
        # Only a weak reference is kept
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        else:
            handler = weakref.ref(handler)
        self.pygletEventHandlers[event_type].append(handler)

    def addRateLimitedPygletListener(self, event_type, handler):
        if self.cfg["debug.events.register"]:
            print("Registered Rate Limited Event: %s Handler: %s" % (event_type, handler))
        if event_type not in self.rlPygletEventHandlers:
            self.rlPygletEventHandlers[event_type] = []
        # Only a weak reference is kept
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        else:
            handler = weakref.ref(handler)
        self.rlPygletEventHandlers[event_type].append(handler)

    def _pumpRateLimitedEvents(self):
        for event_type in self.rlPygletEventHandlers:
            if self.rlPygletEventHandlersTriggered[event_type]:
                self.rlPygletEventHandlersTriggered[event_type] = False

                if event_type in self.rlPygletEventHandlers:
                    args = list(self.rlPygletEventHandlersParams.get(event_type, []))

                    for whandler in self.rlPygletEventHandlers[event_type]:
                        # This allows for proper collection of deleted handler methods by using weak references
                        handler = whandler()
                        if handler is None:
                            del self.rlPygletEventHandlers[event_type][
                                self.rlPygletEventHandlers[event_type].index(whandler)]
                        handler(*args)
    
    # For compatibility, deprecated
    handleEvent = sendPygletEvent
    registerEventHandler = addPygletListener
    registerRateLimitedEventHandler = addRateLimitedPygletListener
    
    def sendEvent(self,event,data=None):
        """
        Sends an event with attached data.
        
        ``event`` should be a string of format ``<namespace>:<category1>.<subcategory2>.<name>``\\ .
        There may be an arbitrary amount of subcategories. Also note that this
        format is not strictly enforced, but rather recommended by convention.
        
        ``data`` may be any Python Object, but it usually is a dictionary containing relevant parameters.
        For example, most built-in events use a dictionary containing at least the ``peng`` key set to an instance of this class.
        
        If there are no handlers for the event, a corresponding message will be printed to the log file.
        To prevent spam, the maximum amount of ignored messages can be configured via :confval:`events.maxignore` and defaults to 3.
        
        If the config value :confval:`debug.events.dumpfile` is a file path, the event type will be added to an internal list and be saved to the given file during program exit.
        """
        if self.cfg["debug.events.dumpfile"]!="" and event not in self.event_list:
            self.event_list.add(event)
        if event not in self.eventHandlers:
            if event not in self.events_ignored or self.events_ignored[event]<=self.cfg["events.maxignore"]: # Prevents spamming logfile with ignored event messages
                # TODO: write to logfile
                # Needs a logging module first...
                self.events_ignored[event] = self.events_ignored.get(event,0)+1
            return
        
        for handler in self.eventHandlers[event]:
            f = handler[0]
            try:
                f(event,data)
            except Exception:
                if not handler[1]:
                    raise
                else:
                    # TODO: write to logfile
                    if self.cfg["events.removeonerror"]:
                        self.delEventListener(event,f)
    
    def addEventListener(self,event,func,raiseErrors=False):
        """
        Adds a handler to the given event.
        
        A event may have an arbitrary amount of handlers, though assigning too
        many handlers may slow down event processing.
        
        For the format of ``event``\\ , see :py:meth:`sendEvent()`\\ .
        
        ``func`` is the handler which will be executed with two arguments, ``event_type`` and ``data``\\ , as supplied to :py:meth:`sendEvent()`\\ .
        
        If ``raiseErrors`` is True, exceptions caused by the handler will be re-raised.
        Defaults to ``False``\\ .
        """
        if not isinstance(event,str):
            raise TypeError("Event types must always be strings")
        
        if event not in self.eventHandlers:
            self.eventHandlers[event]=[]
        self.eventHandlers[event].append([func,raiseErrors])
    def delEventListener(self,event,func):
        """
        Removes the given handler from the given event.
        
        If the event does not exist, a :py:exc:`NameError` is thrown.
        
        If the handler has not been registered previously, also a :py:exc:`NameError` will be thrown.
        """
        if event not in self.eventHandlers:
            raise NameError("No handlers exist for event %s"%event)
        if [func,True] in self.eventHandlers[event]:
            del self.eventHandlers[event][self.eventHandlers[event].index(func)]
        elif [func,False] in self.eventHandler[event]:
            del self.eventHandlers[event][self.eventHandlers[event].index(func)]
        else:
            raise NameError("This handler is not registered for event %s"%event)
        if self.eventHandlers[event] == []:
            del self.eventHandlers[event]

    def on_mouse_motion(self, x, y, dx, dy):
        _, _, odx, ody = self.rlPygletEventHandlersParams["on_mouse_motion"]
        self.rlPygletEventHandlersParams["on_mouse_motion"] = (x, y, dx+odx, dy+ody)
        self.rlPygletEventHandlersTriggered["on_mouse_motion"] = True

    def on_resize(self, width, height):
        self.rlPygletEventHandlersParams["on_resize"] = (width, height)
        self.rlPygletEventHandlersTriggered["on_resize"] = True
    
    def handler_exit(self,event,data):
        if self.cfg["debug.events.dumpfile"]!="":
            with open(self.cfg["debug.events.dumpfile"],"w") as f:
                f.write("\n".join(sorted(list(self.event_list))))
    handler_exit.__noautodoc__ = True

class HeadlessPeng(object):
    """
    Variant of peng that should work without having pyglet installed.
    
    This class is intended for use in servers as a drop-in replacement for the normal engine class.
    
    Note that this class is only in its beginnings and should not be used yet.
    """
    def __init__(self,cfg={}):
        if "rsrc.enable" not in cfg:
            cfg["rsrc.enable"]=False
        super(HeadlessPeng,self).__init__(cfg)
