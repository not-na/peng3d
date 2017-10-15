#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

__all__ = [
    "WatchingList",
    "register_pyglet_handler",
    "ActionDispatcher",
    ]

import sys
import weakref
import threading

try:
    import bidict
except ImportError:
    HAVE_BIDICT = False
else:
    HAVE_BIDICT = True

from .gui import *

class WatchingList(list):
    """
    Subclass of :py:func:`list` implementing a watched list.
    
    A WatchingList will call the given callback with a reference to itself whenever it is modified.
    Internally, the callback is stored as a weak reference, meaning that the creator should keep a reference around.
    
    This class is used in :py:class:`peng3d.gui.widgets.BasicWidget()` to allow for modifying single coordinates of the pos and size properties.
    """
    def __init__(self,l,callback=lambda:None):
        self.callback = weakref.WeakMethod(callback)
        super(WatchingList,self).__init__(l)
    def __setitem__(self,*args):
        super(WatchingList,self).__setitem__(*args)
        c = self.callback()(self)

def register_pyglet_handler(peng,func,event,raiseErrors=False):
    peng.addEventListener("pyglet:%s"%event,(lambda data:func(*data["args"])),raiseErrors)

class ActionDispatcher(object):
    def addAction(self,action,func,*args,**kwargs):
        """
        Adds a callback to the specified action.
        
        All other positional and keyword arguments will be stored and passed to the function upon activation.
        """
        if not hasattr(self,"actions"):
            self.actions = {}
        if action not in self.actions:
            self.actions[action] = []
        self.actions[action].append((func,args,kwargs))
    def doAction(self,action):
        """
        Helper method that calls all callbacks registered for the given action.
        """
        if not hasattr(self,"actions"):
            return
        for f,args,kwargs in self.actions.get(action,[]):
            f(*args,**kwargs)


class SmartRegistry(object):
    def __init__(self,data=None,reuse_ids=False,start_id=0,max_id=float("inf"),default_reg=None):
        # TODO: fix max_id being a float by default
        assert HAVE_BIDICT
        
        self._data = data if data is not None else {}
        
        self.reuse_ids = reuse_ids
        # if true, new ids will be assigned from lowest available id
        # if false, an internal counter is used
        
        self.start_id = start_id
        self.max_id = max_id
        
        self.id_lock = threading.Lock()
        self.registry_lock = threading.Lock()
        
        if "reg" not in self._data:
            default_reg = default_reg if default_reg is not None else {}
            if not isinstance(default_reg,dict):
                raise TypeError("Default Registry must be a dictionary")
            # no reg yet, create a new one
            # ID->NAME mapping
            self._data["reg"] = default_reg
        for k in self._data["reg"].keys():
            if not isinstance(k,int):
                raise TypeError("All keys must be integers")
        for v in self._data["reg"].values():
            if not isinstance(v,str):
                raise TypeError("All values must be strings")
        self._data["reg"] = bidict.bidict(self._data["reg"])
        if not self.reuse_ids and "next_id" not in self._data:
            if self._data.get("reg",{}) != {}:
                # already data there, find highest id +1
                self._data["next_id"]=max(max(self._data["reg"].keys())+1,start_id)
            else:
                # no data there, use start_id
                self._data["next_id"]=self.start_id
    
    def genNewID(self):
        if self.reuse_ids:
            i = self.start_id
            while True:
                if i not in self._data["reg"]:
                    assert i<=self.max_id
                    return i # no need to change any variables
                i+=1
        else:
            with self.id_lock:
                # new id creation in lock, to avoid issues with multiple threads
                i = self._data["next_id"]
                assert i<=self.max_id
                self._data["next_id"]+=1
            return i
    
    def register(self,name,force_id=None):
        with self.registry_lock:
            if force_id is None:
                new_id = self.genNewID()
            else:
                new_id = force_id
            self._data["reg"][new_id]=name
            return new_id
    
    def normalizeID(self,in_id):
        if isinstance(in_id,int):
            assert in_id in self._data["reg"]
            return in_id
        elif isinstance(in_id,str):
            assert in_id in self._data["reg"].inv
            return self._data["reg"].inv[in_id]
        else:
            raise TypeError("Only int and str can be converted to IDs")
    def normalizeName(self,in_name):
        if isinstance(in_name,str):
            assert in_name in self._data["reg"].inv
            return in_name
        elif isinstance(in_name,int):
            assert in_name in self._data["reg"]
            return self._data["reg"][in_name]
        else:
            raise TypeError("Only int and str can be converted to names")
    
    @property
    def data(self):
        d = self._data
        d["reg"]=dict(d["reg"])
        return d
    
    def __getitem__(self,key):
        # to access registry as reg[obj] -> name
        return self.normalizeName(key)
    
    def __setitem(self,key,value):
        # None may be used as value for auto generation
        # to access registry as reg[name]=id
        self.register(key,value)
    
    def __in__(self,value):
        return value in self._data["reg"] or value in self._data["reg"].inv
