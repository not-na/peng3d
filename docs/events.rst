
Events used by Peng3d
=====================

.. seealso::
   
   This document describes the events used by peng3d, see
   :py:meth:`peng3d.peng.Peng.sendEvent()` for information about the event system itself.

Note that there is no completely safe way to get a list of all events used by an
application, but you should get most events by setting the config value
``debug.events.dumpfile`` to a valid file name and running the application in
question. Make sure to trigger all events, or else they may not appear in the list.

This document is sectioned after the categories of events used.

Note that many applications will add their own events, which should be listed in their documentation.

Peng3d Events using :py:meth:`sendEvent()`
------------------------------------------

Events listed here can be sent via the :py:meth:`~peng3d.peng.Peng.sendEvent()`
method and be received via :py:meth:`~peng3d.peng.Peng.addEventListener()`\ .

If possible, this system should be used, as it is better and has many improvements over previous systems.

Most of these events use a dictionary containing at least the ``peng`` key as their data parameter.

Special events
^^^^^^^^^^^^^^

These events are special and should not be sent manually, they are mostly for backwards-compatibility.

.. peng3d:event:: peng3d:pyglet
   
   Special event sent by :py:meth:`~peng3d.peng.Peng.sendPygletEvent()` for compatibility.
   
   Additional parameters:
   
   ``args`` is a list of the given parameters.
   
   ``window`` is the window this event originated from.
   
   ``src`` is the object this event was sent via.
   
   ``event_type`` is the pyglet event type.
   
   .. seealso::
      
      See :peng3d:event:`pyglet:*` for another way of accessing pyglet events.

.. peng3d:event:: pyglet:*
   
   Special event sent by :py:meth:`~peng3d.peng.Peng.sendPygletEvent()` for compatibility.
   
   See :peng3d:event:`peng3d:pyglet` for more information on the given parameters.

``peng3d:peng.*`` Events Category
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These events are typically sent by the main :py:class:`~peng3d.peng.Peng()` instance.

.. peng3d:event:: peng3d:peng.run
   
   Triggered once when calling :py:meth:`~peng3d.peng.Peng.run()` just before starting the event loop.
   
   Additional parameters are ``window`` set to the main window object and
   ``evloop`` set to the argument of the same name.

.. peng3d:event:: peng3d:peng.exit
   
   Triggered once the pyglet event loop exits.
   
   Note that the calling method may cause the program to continue running.
   
   This event has no additional parameters.

``peng3d:window.*`` Events Category
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These events are sent to mark changes to an instance of :py:class:`~peng3d.window.PengWindow()`\ .

Note that some of these events are not sent by the window itself and do not require a window to exist.

.. peng3d:event:: peng3d:window.create.pre
                  peng3d:window.create
                  peng3d:window.create.post
   
   These events are sent when the main window is created.
   
   The event :peng3d:event:`peng3d:window.create.pre` has the additional
   parameter ``cls`` containing the class used to create the window.
   
   The events :peng3d:event:`peng3d:window.create` and :peng3d:event:`peng3d:window.create.post`
   both have the additional parameter ``window`` set to the window object.
   
   Note that the ``window`` attribute of :py:class:`~peng3d.peng.Peng()` is only
   available after the handling of :peng3d:event:`peng3d:window.create` has finished.

.. peng3d:event:: peng3d:window.menu.add
   
   Triggered whenever a menu is added to the window.
   
   Additional parameters are ``window`` set to the window object and ``menu`` set to the menu object.

.. peng3d:event:: peng3d:window.menu.change
   
   Triggered whenever the active menu is changed.
   
   This event is sent after other event handlers have finished processing.
   
   Additional parameters:
   
   ``window`` is the current window object.
   
   ``old`` is the name of the old menu. This may be ``None`` if there was no active menu.
   
   ``menu`` is the name of the new menu.

.. peng3d:event:: peng3d:window.toggle_exclusive
   
   Triggered whenever the mouse exclusivity is changed via :py:meth:`~peng3d.window.PengWindow.toggle_exclusivity()`\ .
   
   Additional parameters are ``window`` set to the window object and ``exclusive`` set to the current exclusivity state.

``peng3d:rsrc.*`` Events Category
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These events are sent by the :py:class:`~peng3d.resource.ResourceManager()` to
signal that either the manager itself was modified or a resource was changed.

.. peng3d:event:: peng3d:rsrc.init.pre
                  peng3d:rsrc.init
                  peng3d:rsrc.init.post
   
   These events are sent when the resource manager is first initialized.
   
   The event :peng3d:event:`peng3d:rsrc.init.pre` has the additional
   parameter ``basepath`` containing the base path of the new resource manager.
   
   The events :peng3d:event:`peng3d:rsrc.init` and :peng3d:event:`peng3d:rsrc.init.post`
   both have the additional parameter ``rsrcMgr`` set to the newly created resource manager.
   
   Note that the ``resourceMgr`` attribute of :py:class:`~peng3d.peng.Peng()`
   is only available after the handling of :peng3d:event:`peng3d:rsrc.init` has finished.

.. peng3d:event:: peng3d:rsrc.category.add
   
   Sent when a new resource category is added.
   
   The additional parameter ``category`` is set to the name of the new category.

.. peng3d:event:: peng3d:rsrc.tex.load
   
   Sent when a texture resource is first loaded.
   
   Additional parameters are ``name`` and ``category`` set to their corresponding
   arguments given to :py:meth:`~peng3d.resource.ResourceManager.loadTex()`\ .

.. peng3d:event:: peng3d:rsrc.model.load
   
   Sent when a model resource is first loaded.
   
   Additional parameters are ``name`` set to the name of the model.

.. _events-i18n:

``peng3d:i18n.*`` Events Category
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. seealso::
   
   See :py:class:`~peng3d.i18n.TranslationManager()` for more information about the translation system.

.. peng3d:event:: peng3d.i18n.set_lang
   
   Sent whenever the default language is set.
   
   Note that this event is sent regardless of whether or not the language actually changed.
   
   Additional parameters are ``i18n``\ , set to the translation manager, and ``lang``
   set to the new language.


``peng3d:keybind.*`` Events Category
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These events usually mark an event related to a specific key combination.

.. seealso::
   
   See :py:class:`~peng3d.keybind.KeybindHandler()` for more information on the keybind system.

.. peng3d:event:: peng3d:keybind.add
   
   Triggered when a keybind is added to the system.
   
   Additional parameters are all arguments given to :py:meth:`~peng3d.keybind.KeybindHandler.add()`\ .

.. peng3d:event:: peng3d:keybind.change
   
   Triggered when a keybind is changed.
   
   Additional parameters are all arguments given to :py:meth:`~peng3d.keybind.KeybindHandler.changeKeybind()`\ .

.. peng3d:event:: peng3d:keybind.combo
                  peng3d:keybind.combo.press
                  peng3d:keybind.combo.release
   
   These events are triggered whenever a key combination is detected.
   
   Note that this event will be sent regardless of whether or not there are any
   handlers registered for the keybind in question.
   
   :peng3d:event:`peng3d:keybind.combo` is always sent, and depending on the
   ``release`` flag, either :peng3d:event:`peng3d:keybind.combo.press` or
   :peng3d:event:`peng3d:keybind.combo.release` is also sent.
   
   Additional parameters are the same as the arguments given to :py:meth:`~peng3d.keybind.KeybindHandler.handle_combo()`\ .

Pyglet Events using :py:meth:`sendPygletEvent()`
------------------------------------------------

Events listed here can be sent via the :py:meth:`~peng3d.peng.Peng.sendPygletEvent()`
method and be received via :py:meth:`~peng3d.peng.Peng.addPygletListener()`\ .

There are also several events sent by pyglet itself, see the `Pyglet Docs <http://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/index.html>`_ for more information.

.. todo::
   
   Add docs for custom pyglet events.
