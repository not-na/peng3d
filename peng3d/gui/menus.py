#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  menus.py
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
    "DialogSubMenu",
    "ConfirmSubMenu","TextSubMenu",
    ]

import pyglet

from . import SubMenu
from . import text
from . import button

class DialogSubMenu(SubMenu):
    DEFAULT_LABELS = {
        "label_main":"Default Text",
        "label_ok":"OK",
        }
    def __init__(self,name,menu,window,peng,
                borderstyle="oldshadow",
                **kwargs # for label_main etc.
                ):
        super(DialogSubMenu,self).__init__(name,menu,window,peng)
        
        self.prev_submenu = None
        self.borderstyle = borderstyle
        
        labels = {}
        labels.update(self.DEFAULT_LABELS)
        labels.update(kwargs)
        
        self.add_widgets(**labels)
    
    def add_widgets(self,**kwargs):
        if "label_main" in kwargs:
            self.add_label_main(kwargs["label_main"])
        if "label_ok" in kwargs:
            self.add_btn_ok(kwargs["label_ok"])
    
    def add_label_main(self,label_main):
        # Main Label
        self.wlabel_main = text.Label("label_main",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,sh/2-bh/2),
                        size=[0,0],
                        label=label_main,
                        #multiline=True, # TODO: implement multine dialog
                        )
        self.wlabel_main.size = lambda sw,sh: (sw,self.wlabel_main._label.font_size)
        self.addWidget(self.wlabel_main)
    
    def add_btn_ok(self,label_ok):
        # OK Button
        self.wbtn_ok = button.Button("btn_ok",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_ok,
                        borderstyle=self.borderstyle
                        )
        self.wbtn_ok.size = lambda sw,sh: (self.wbtn_ok._label.font_size*8,self.wbtn_ok._label.font_size*2)
        self.addWidget(self.wbtn_ok)
        
        def f():
            self.doAction("click_ok")
            self.exitDialog()
        self.wbtn_ok.addAction("click",f)
        
    @property
    def label_main(self):
        # no check for initialized label, NameError should be good enough to debug
        return self.wlabel_main.label
    @label_main.setter
    def label_main(self,value):
        self.wlabel_main.label = value
        self.doAction("label_main_change")
    
    @property
    def label_ok(self):
        return self.wbtn_ok.label
    @label_ok.setter
    def label_ok(self,value):
        self.wbtn_ok.label = value
        self.doAction("label_ok_change")
    
    def on_enter(self,old):
        if self.menu.activeSubMenu==self.menu:
            raise RuntimeError("Cannot open a dialog twice")
        self.doAction("enter")
        self.prev_submenu = old # name or None
    
    def exitDialog(self):
        # to allow easy hooking
        self.doAction("exit")
        if self.prev_submenu is not None:
            # change back to the previous submenu
            # could in theory form a stack if one dialog opens another
            self.menu.changeSubMenu(self.prev_submenu)
        self.prev_submenu = None
    
    def activate(self):
        if self.menu.activeSubMenu==self.name:
            raise RuntimeError("Cannot open a dialog twice")
        # on_enter will be called automatically to store previous submenu
        self.menu.changeSubMenu(self.name)
    

class ConfirmSubMenu(DialogSubMenu):
    DEFAULT_LABELS = {
        "label_main":"Are you sure?",
        "label_confirm":"Confirm",
        "label_cancel":"Cancel",
        }
    def add_widgets(self,**kwargs):
        super(ConfirmSubMenu,self).add_widgets(**kwargs)
        if "label_confirm" in kwargs:
            self.add_btn_confirm(kwargs["label_confirm"])
        if "label_cancel" in kwargs:
            self.add_btn_cancel(kwargs["label_cancel"])
    
    def add_btn_confirm(self,label_confirm):
        # Confirm Button
        self.wbtn_confirm = button.Button("btn_confirm",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw-4,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_confirm,
                        borderstyle=self.borderstyle
                        )
        self.wbtn_confirm.size = lambda sw,sh: (self.wbtn_confirm._label.font_size*8,self.wbtn_confirm._label.font_size*2)
        self.addWidget(self.wbtn_confirm)
        
        def f():
            self.doAction("confirm")
            self.exitDialog()
        self.wbtn_confirm.addAction("click",f)
    
    def add_btn_cancel(self,label_cancel):
        # Cancel Button
        self.wbtn_cancel = button.Button("btn_cancel",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2+4,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_cancel,
                        borderstyle=self.borderstyle
                        )
        self.wbtn_cancel.size = lambda sw,sh: (self.wbtn_cancel._label.font_size*8,self.wbtn_cancel._label.font_size*2)
        self.addWidget(self.wbtn_cancel)
        
        def f():
            self.doAction("cancel")
            self.exitDialog()
        self.wbtn_cancel.addAction("click",f)
    
    @property
    def label_confirm(self):
        return self.wbtn_confirm.label
    @label_confirm.setter
    def label_confirm(self,value):
        self.wbtn_confirm.label = value
        self.doAction("label_confirm_change")
    
    @property
    def label_cancel(self):
        return self.wbtn_cancel.label
    @label_cancel.setter
    def label_cancel(self,value):
        self.wbtn_cancel.label = value
        self.doAction("label_cancel_change")

class TextSubMenu(DialogSubMenu):
    DEFAULT_LABELS = {
        "label_main":"Default Text",
        # no button needed, timer does the rest
        }
    def __init__(self,name,menu,window,peng,
                borderstyle="oldshadow",
                timeout=10,
                **kwargs
                ):
        super(TextSubMenu,self).__init__(name,menu,window,peng,borderstyle,**kwargs)
        self.timeout = timeout
    
    def on_enter(self,old):
        super(TextSubMenu,self).on_enter(old)
        
        if self.timeout!=-1:
            pyglet.clock.schedule_once(lambda dt:self.exitDialog(),self.timeout)
