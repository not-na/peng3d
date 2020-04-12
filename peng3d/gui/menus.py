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

"""
Menus are special submenus that act like modal dialogs.

They include glue code that automatically switches back to the previous submenu
after they are left. Note that this will cuase the :py:meth:`SubMenu.on_enter()`
method to be called again.

Since these menus are internally implemented as submenus, they are specific to their
:py:class:`Menu`\ , which must be active to be able to use the dialog.

Customization
-------------

Menus are customizable via several different means.

If you just want to change the appearance or label of a part of the menu, you can
use keyword arguments while initializing the class.
For example, setting the ``label_main`` argument to the string ``Hello World!`` the
main label or title of the dialog will now display ``Hello World!`` instead of its default
value.
What exact arguments are supported differs from dialog to dialog.

Note that sometimes specific labels are supported, but not used by default.
Just setting these to anything may cause GUI components to be rendered that
should not be there.

It is also possible for most of these values to be set on-the-fly via properties
on the object they belong to.

For example, the :py:attr:`DialogSubMenu.label_main` property may be set to change
the main label even while the dialog is active.

Note that the values accessible via keyword arguments and properties may differ.
This depends on the dialog implementing them.

For clarity, these keyword arguments will from now on be called "labels". This also
includes labels that are not strictly text, like the maximum value of a progressbar.
"""

__all__ = [
    "DialogSubMenu",
    "ConfirmSubMenu","TextSubMenu",
    "ProgressSubMenu","AdvancedProgressSubMenu",
    ]

import pyglet

from . import SubMenu
from . import text
from . import button
from . import slider

class DialogSubMenu(SubMenu):
    """
    Base Dialog Class.
    
    This class acts as a base class for all other dialog submenus.
    
    When the dialog is entered, the :py:attr:`prev_submenu` attribute will be set
    to the name of the previous submenu. This attribute is later used when exiting
    the dialog.
    
    Dialog submenus also support the basic actions used by all submenus, e.g.
    ``enter`` and ``exit``\ . Additionally, many dialogs also add actions for whenever
    a label is changed or the dialog is exited through a special means, e.g. pressing
    a specific button of multiple presented.
    
    If used by itself, it will display a text centered on the screen with a button
    below it. Clicking the button will cause the dialog to exit and also the
    additional ``click_ok`` action to be fired.
    
    The labels supported by default are ``label_main``\ , which defaults to ``Default Text``
    and is recommended to always be customized, and ``label_ok``\, which defaults to ``OK``
    and may be left as-is.
    
    Subclasses may override these defaults by setting the keys of the same name in the
    ``DEFAULT_LABELS`` class attribute. Note that any unchanged labels must also be declared
    when overwriting any labels, or they may not be displayed.
    
    Widgets and their initializers are stored in the :py:data:`WIDGETS` class attribute,
    see :py:meth:`add_widgets()` for more information.
    """
    DEFAULT_LABELS = {
        "label_main":"Default Text",
        "label_ok":"OK",
        }
    WIDGETS = {
        "label_main":"add_label_main",
        "label_ok":"add_btn_ok",
    }
    def __init__(self,name,menu,window,peng,
                borderstyle=None,
                font_size=None, font=None,
                font_color=None,
                multiline=False,
                **kwargs # for label_main etc.
                ):
        super(DialogSubMenu,self).__init__(name,menu,window,peng)

        self.font = font if font is not None else self.menu.font
        self.font_size = font_size if font_size is not None else self.menu.font_size
        self.font_color = font_color if font_color is not None else self.menu.font_color
        self.borderstyle = borderstyle if borderstyle is not None else self.menu.borderstyle

        self.multiline = multiline
        
        self.prev_submenu = None
        
        labels = {}
        labels.update(self.DEFAULT_LABELS)
        labels.update(kwargs)
        self.labels = kwargs
        self.kwargs = kwargs
        
        self.add_widgets(**labels)
    
    def add_widgets(self,**kwargs):
        """
        Called by the initializer to add all widgets.
        
        Widgets are discovered by searching through the :py:attr:`WIDGETS` class attribute.
        If a key in :py:attr:`WIDGETS` is also found in the keyword arguments and
        not none, the function with the name given in the value of the key will
        be called with its only argument being the value of the keyword argument.
        
        For more complex usage scenarios, it is also possible to override this method
        in a subclass, but the original method should always be called to ensure
        compatibility with classes relying on this feature.
        """
        for name,fname in self.WIDGETS.items():
            if name in kwargs and kwargs[name] is not None:
                assert hasattr(self,fname)
                assert callable(getattr(self,fname))
                getattr(self,fname)(kwargs[name])
    
    def add_label_main(self,label_main):
        """
        Adds the main label of the dialog.
        
        This widget can be triggered by setting the label ``label_main`` to a string.
        
        This widget will be centered on the screen.
        """
        # Main Label
        self.wlabel_main = text.Label("label_main",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,sh/2-bh/2),
                        size=[0,0],
                        label=label_main,
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        multiline=self.multiline,
                        )
        self.wlabel_main.size = lambda sw,sh: (sw,self.wlabel_main._label.font_size)
        self.addWidget(self.wlabel_main)
    
    def add_btn_ok(self,label_ok):
        """
        Adds an OK button to allow the user to exit the dialog.
        
        This widget can be triggered by setting the label ``label_ok`` to a string.
        
        This widget will be mostly centered on the screen, but below the main label
        by the double of its height.
        """
        # OK Button
        self.wbtn_ok = button.Button("btn_ok",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_ok,
                        borderstyle=self.borderstyle,
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        )
        self.wbtn_ok.size = lambda sw,sh: (self.wbtn_ok._label.font_size*8,self.wbtn_ok._label.font_size*2)
        self.addWidget(self.wbtn_ok)
        
        def f():
            self.doAction("click_ok")
            self.exitDialog()
        self.wbtn_ok.addAction("click",f)
        
    @property
    def label_main(self):
        """
        Property that proxies the ``label_main`` label.
        
        Setting this property will cause the ``label_main_change`` action to trigger.
        
        Note that trying to access this property if the widget is not used may cause
        an error.
        """
        # no check for initialized label, NameError should be good enough to debug
        return self.wlabel_main.label
    @label_main.setter
    def label_main(self,value):
        self.wlabel_main.label = value
        self.doAction("label_main_change")
    
    @property
    def label_ok(self):
        """
        Property that proxies the ``label_ok`` label.
        
        Setting this property will cause the ``label_ok_change`` action to trigger.
        
        Note that trying to access this property if the widget is not used may cause
        an error.
        """
        return self.wbtn_ok.label
    @label_ok.setter
    def label_ok(self,value):
        self.wbtn_ok.label = value
        self.doAction("label_ok_change")
    
    def on_enter(self,old):
        if self.menu.activeSubMenu==self.menu:
            raise RuntimeError("Cannot open a dialog twice")
        self.prev_submenu = old # name or None
    
    def exitDialog(self):
        """
        Helper method that exits the dialog.
        
        This method will cause the previously active submenu to activate.
        """
        if self.prev_submenu is not None:
            # change back to the previous submenu
            # could in theory form a stack if one dialog opens another
            self.menu.changeSubMenu(self.prev_submenu)
        self.prev_submenu = None
    
    def activate(self):
        """
        Helper method to enter the dialog.
        
        Calling this method will simply cause the dialog to become the active submenu.
        
        Note that is not necessary to call this method over :py:meth:`changeSubMenu()`\ , 
        as the storing of the previous submenu is done elsewhere.
        """
        # error checking done indirectly by on_enter
        # on_enter will be called automatically to store previous submenu
        self.menu.changeSubMenu(self.name)
    

class ConfirmSubMenu(DialogSubMenu):
    """
    Dialog that allows the user to confirm or cancel an action.
    
    By default, the OK button will be hidden and the ``label_main`` will be set
    to ``Are you sure?``\ .
    
    Clicking the confirm button will cause the ``confirm`` action to trigger, while
    the cancel button will cause the ``cancel`` action to trigger.
    """
    DEFAULT_LABELS = {
        "label_main":"Are you sure?",
        "label_confirm":"Confirm",
        "label_cancel":"Cancel",
        }
    WIDGETS = {
        **DialogSubMenu.WIDGETS,
        "label_confirm":"add_btn_confirm",
        "label_cancel":"add_btn_cancel",
        }
    
    def add_btn_confirm(self,label_confirm):
        """
        Adds a confirm button to let the user confirm whatever action they were presented with.
        
        This widget can be triggered by setting the label ``label_confirm`` to a string.
        
        This widget will be positioned slightly below the main label and to the left
        of the cancel button.
        """
        # Confirm Button
        self.wbtn_confirm = button.Button("btn_confirm",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw-4,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_confirm,
                        borderstyle=self.borderstyle,
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        )
        self.wbtn_confirm.size = lambda sw,sh: (self.wbtn_confirm._label.font_size*8,self.wbtn_confirm._label.font_size*2)
        self.addWidget(self.wbtn_confirm)
        
        def f():
            self.doAction("confirm")
            self.exitDialog()
        self.wbtn_confirm.addAction("click",f)
    
    def add_btn_cancel(self,label_cancel):
        """
        Adds a cancel button to let the user cancel whatever choice they were given.
        
        This widget can be triggered by setting the label ``label_cancel`` to a string.
        
        This widget will be positioned slightly below the main label and to the right
        of the confirm button.
        """
        # Cancel Button
        self.wbtn_cancel = button.Button("btn_cancel",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2+4,sh/2-bh/2-bh*2),
                        size=[0,0],
                        label=label_cancel,
                        borderstyle=self.borderstyle,
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        )
        self.wbtn_cancel.size = lambda sw,sh: (self.wbtn_cancel._label.font_size*8,self.wbtn_cancel._label.font_size*2)
        self.addWidget(self.wbtn_cancel)
        
        def f():
            self.doAction("cancel")
            self.exitDialog()
        self.wbtn_cancel.addAction("click",f)
    
    @property
    def label_confirm(self):
        """
        Property that proxies the ``label_confirm`` label.
        
        Setting this property will cause the ``label_confirm_change`` action to trigger.
        
        Note that trying to access this property if the widget is not used may cause
        an error.
        """
        return self.wbtn_confirm.label
    @label_confirm.setter
    def label_confirm(self,value):
        self.wbtn_confirm.label = value
        self.doAction("label_confirm_change")
    
    @property
    def label_cancel(self):
        """
        Property that proxies the ``label_cancel`` label.
        
        Setting this property will cause the ``label_cancel_change`` action to trigger.
        
        Note that trying to access this property if the widget is not used may cause
        an error.
        """
        return self.wbtn_cancel.label
    @label_cancel.setter
    def label_cancel(self,value):
        self.wbtn_cancel.label = value
        self.doAction("label_cancel_change")

class TextSubMenu(DialogSubMenu):
    """
    Dialog without user interaction that can automatically exit after a certain amount of time.
    
    This dialog accepts the ``timeout`` keyword argument, which may be set to any
    time in seconds to delay before exiting the dialog. A value of ``-1`` will cause
    the dialog to never exit on its own.
    
    Note that the user will not be able to exit this dialog and may believe the program
    is hanging if not assured otherwise. It is thus recommended to use the :py:class:`ProgressSubMenu`
    dialog instead, especially for long-running operations.
    """
    DEFAULT_LABELS = {
        "label_main":"Default Text",
        # no button needed, timer does the rest
        }
    def __init__(self,name,menu,window,peng,
                borderstyle=None,
                timeout=10,
                **kwargs
                ):
        super(TextSubMenu,self).__init__(name,menu,window,peng,borderstyle,**kwargs)
        self.timeout = timeout
    
    def on_enter(self,old):
        super(TextSubMenu,self).on_enter(old)
        
        if self.timeout!=-1:
            pyglet.clock.schedule_once(lambda dt:self.exitDialog(),self.timeout)

class ProgressSubMenu(DialogSubMenu):
    """
    Dialog without user interaction displaying a progressbar.
    
    By default, the progressbar will range from 0-100, effectively a percentage.
    
    The :py:attr:`auto_exit` attribute may be set to control whether or not the dialog
    will exit automatically when the maximum value is reached.
    """
    DEFAULT_LABELS = {
        "label_main":"Loading...",
        "label_progressbar":"{percent:.1}%",
        # TODO: actually implement the progress_* labels
        "progress_n":0, # should be updated on-the-fly through property progress_n
        "progress_nmin":0,
        "progress_nmax":100, # basically equal to percentages
        }
    WIDGETS = {
        **DialogSubMenu.WIDGETS,
        "label_progressbar":"add_progressbar",
        }
    auto_exit = False
    """
    Controls whether or not the dialog will exit automatically after the maximum
    value has been reached.
    """
    
    def add_progressbar(self,label_progressbar):
        """
        Adds a progressbar and label displaying the progress within a certain task.
        
        This widget can be triggered by setting the label ``label_progressbar`` to
        a string.
        
        The progressbar will be displayed centered and below the main label.
        The progress label will be displayed within the progressbar.
        
        The label of the progressbar may be a string containing formatting codes
        which will be resolved via the ``format()`` method.
        
        Currently, there are six keys available:
        
        ``n`` and ``value`` are the current progress rounded to 4 decimal places.
        
        ``nmin`` is the minimum progress value rounded to 4 decimal places.
        
        ``nmax`` is the maximum progress value rounded to 4 decimal places.
        
        ``p`` and ``percent`` are the percentage value that the progressbar is completed
        rounded to 4 decimal places.
        
        By default, the progressbar label will be ``{percent}%`` displaying the percentage
        the progressbar is complete.
        """
        # Progressbar
        self.wprogressbar = slider.Progressbar("progressbar",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,self.wlabel_main.pos[1]-bh*1.5),
                        size=[0,0],
                        #label=label_progressbar # TODO: add label
                        borderstyle=self.borderstyle
                        )
        self.addWidget(self.wprogressbar)
        
        # Progress Label
        self.wprogresslabel = text.Label("progresslabel",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,self.wprogressbar.pos[1]+8),
                        size=[0,0],
                        label="", # set by update_progressbar()
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        )
        self.wprogresslabel.size = lambda sw,sh: (sw,self.wprogresslabel._label.font_size)
        self.addWidget(self.wprogresslabel)
        
        self.wprogressbar.size = lambda sw,sh: (sw*0.8,self.wprogresslabel._label.font_size+10)
        
        self._label_progressbar = label_progressbar
        
        if getattr(label_progressbar,"_dynamic",False):
            def f():
                self.label_progressbar = str(label_progressbar)
            self.peng.i18n.addAction("setlang",f)
        
        self.wprogressbar.addAction("progresschange",self.update_progressbar)
        
        self.update_progressbar()
    
    def update_progressbar(self):
        """
        Updates the progressbar by re-calculating the label.
        
        It is not required to manually call this method since setting any of the
        properties of this class will automatically trigger a re-calculation.
        """
        n,nmin,nmax = self.wprogressbar.n,self.wprogressbar.nmin,self.wprogressbar.nmax
        if (nmax-nmin)==0:
            percent = 0 # prevents ZeroDivisionError
        else:
            percent = max(min((n-nmin)/(nmax-nmin),1.),0.)*100
        dat = {"value":round(n,4),"n":round(n,4),"nmin":round(nmin,4),"nmax":round(nmax,4),"percent":round(percent,4),"p":round(percent,4)}
        txt = self._label_progressbar.format(**dat)
        self.wprogresslabel.label = txt
    
    @property
    def progress_n(self):
        """
        Property that proxies the ``progress_n`` label.
        
        Setting this property will cause the progressbar label to be recalculated.
        
        Additionally, if the supplied value is higher than the maximum value and
        :py:attr:`auto_exit` is true, the dialog will exit.
        """
        return self.wprogressbar.n
    @progress_n.setter
    def progress_n(self,value):
        self.wprogressbar.n = value
        self.update_progressbar()
        if self.auto_exit:
            if self.wprogressbar.n>=self.wprogressbar.nmax:
                self.exitDialog()
    
    @property
    def progress_nmin(self):
        """
        Property that proxies the ``progress_nmin`` label.
        
        Setting this property will cause the progressbar label to be recalculated.
        
        Note that setting this property if the widget has not been initialized may
        cause various errors to occur.
        """
        return self.wprogressbar.nmin
    @progress_nmin.setter
    def progress_nmin(self,value):
        self.wprogressbar.nmin = value
        self.update_progressbar()
    
    @property
    def progress_nmax(self):
        """
        Property that proxies the ``progress_nmax`` label.
        
        Setting this property will cause the progressbar label to be recalculated.
        
        Note that setting this property if the widget has not been initialized may
        cause various errors to occur.
        """
        return self.wprogressbar.nmax
    @progress_nmax.setter
    def progress_nmax(self,value):
        self.wprogressbar.nmax = value
        self.update_progressbar()
    
    @property
    def label_progressbar(self):
        """
        Property that proxies the ``label_progressbar`` label.
        
        Setting this property will cause the progressbar label to be recalculated.
        
        Note that setting this property if the widget has not been initialized may
        cause various errors to occur.
        """
        return self.wprogresslabel.label
    @label_progressbar.setter
    def label_progressbar(self,value):
        self._label_progressbar = value
        self.update_progressbar()
    

class AdvancedProgressSubMenu(ProgressSubMenu):
    def add_progressbar(self,label_progressbar):
        """
        Adds a progressbar and label displaying the progress within a certain task.
        
        This widget can be triggered by setting the label ``label_progressbar`` to
        a string.
        
        The progressbar will be displayed centered and below the main label.
        The progress label will be displayed within the progressbar.
        
        The label of the progressbar may be a string containing formatting codes
        which will be resolved via the ``format()`` method.
        
        Currently, there are six keys available:
        
        ``n`` and ``value`` are the current progress rounded to 4 decimal places.
        
        ``nmin`` is the minimum progress value rounded to 4 decimal places.
        
        ``nmax`` is the maximum progress value rounded to 4 decimal places.
        
        ``p`` and ``percent`` are the percentage value that the progressbar is completed
        rounded to 4 decimal places.
        
        By default, the progressbar label will be ``{percent}%`` displaying the percentage
        the progressbar is complete.
        """
        # Progressbar
        self.wprogressbar = slider.AdvancedProgressbar("progressbar",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,self.wlabel_main.pos[1]-bh*1.5),
                        size=[0,0],
                        #label=label_progressbar # TODO: add label
                        borderstyle=self.borderstyle
                        )
        self.addWidget(self.wprogressbar)
        
        # Progress Label
        self.wprogresslabel = text.Label("progresslabel",self,self.window,self.peng,
                        pos=lambda sw,sh, bw,bh: (sw/2-bw/2,self.wprogressbar.pos[1]+8),
                        size=[0,0],
                        label="", # set by update_progressbar()
                        font=self.font, font_size=self.font_size, font_color=self.font_color,
                        )
        self.wprogresslabel.size = lambda sw,sh: (sw,self.wprogresslabel._label.font_size)
        self.addWidget(self.wprogresslabel)
        
        self.wprogressbar.size = lambda sw,sh: (sw*0.8,self.wprogresslabel._label.font_size+10)
        
        self._label_progressbar = label_progressbar
        
        if getattr(label_progressbar,"_dynamic",False):
            def f():
                self.label_progressbar = str(label_progressbar)
            self.peng.i18n.addAction("setlang",f)
        
        self.wprogressbar.addAction("progresschange",self.update_progressbar)
        
        self.update_progressbar()
    
    def addCategory(self,*args,**kwargs):
        """
        Proxy for :py:meth:`~peng3d.gui.slider.AdvancedProgressbar.addCategory()`\ .
        """
        return self.wprogressbar.addCategory(*args,**kwargs)
    def updateCategory(self,*args,**kwargs):
        """
        Proxy for :py:meth:`~peng3d.gui.slider.AdvancedProgressbar.updateCategory()`\ .
        """
        return self.wprogressbar.updateCategory(*args,**kwargs)
    def deleteCategory(self,*args,**kwargs):
        """
        Proxy for :py:meth:`~peng3d.gui.slider.AdvancedProgressbar.deleteCategory()`\ .
        """
        return self.wprogressbar.deleteCategory(*args,**kwargs)
