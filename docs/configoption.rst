
Configuration Options for peng3d
================================

Almost all important settings can be configured per-window or globally via the :py:data:`Peng.cfg` or :py:data:`Window.cfg` attributes.

Graphic Settings/OpenGL Base State
----------------------------------

For most of these graphical settings, it is important to actually use the exact type specified.
For example, you should only pass floats and not integers if the specified type is float.

.. confval:: graphics.clearColor
   
   A 4-tuple of RGBA colors used to clear the window before drawing.
   
   Each Color part should be a float between ``0`` and ``1``\ .
   
   By default, this option is set to ``(0.,0.,0.,1.)``\ .
   
   Be sure to verify that each value is a float, not an integer.

.. confval:: graphics.wireframe
   
   A Boolean value determining the polygon-fill-mode used by OpenGL.
   
   ``True`` results in ``GL_LINE`` being used, while ``False`` will result in ``GL_FILL`` being used.
   
   This option can be used to create a wireframe-like mode.
   
   The default value for this option is ``False``\ .
   
   .. note::
      
      This option is always turned off by :py:meth:`PengWindow.set2d()` but re-enabled by :py:meth:`PengWindow.set3d()` if necessary.

.. confval:: graphics.fieldofview
   
   An float value passed to :py:func:`gluPerspective()` as the first argument.
   
   For more information about this config option, see the GL/GLU documentation.
   
   By default, this option is set to ``65.0``\ .

.. confval:: graphics.nearclip
             graphics.farclip
   
   An float value specifying the near and far clipping plane, respectively.
   
   These clipping planes determine at what point vertices are cut off to save GPU cycles.
   
   By default, :confval:`graphics.nearclip` equals ``0.1`` and :confval:`graphics.farclip` equals ``10000``\ .

Fog settings
^^^^^^^^^^^^

.. confval:: graphics.fogSettings
   
   :py:class:`Config()` object storing the fog-specific settings.
   
   To access fog settings, use ``peng.cfg["graphics.fogSettings"]["<configoption>"]`` as appropriate.

.. confval:: graphics.fogSettings["enable"]
   
   A boolean value activating or deactivating the OpenGL fog.
   
   By default disabled.

.. confval:: graphics.fogSettings["color"]
   
   A 4-Tuple representing an RGB Color.
   
   Note that the values should be 0<=n<=1, not in range(0,256).
   
   For most cases, this value should be set to the clear color, else, visual artifacts may occur.

.. confval:: graphics.fogSettings["start"]
             graphics.fogSettings["end"]
   
   Defines start and end of the fog zone.
   
   The end value should be nearer than the far clipping plane to avoid cut-off vertices.
   
   Each value should be a float and is measured in standard OpenGL units.
   
   By default, the fog starts at 128 units and ends 32 units further out.

Light settings
^^^^^^^^^^^^^^

.. confval:: graphics.lightSettings
   
   :py:class:`Config()` object storing the light settings.
   
   To access light settings, use ``peng.cfg["graphics.lightSettings"]["<configoption>"]`` as appropriate.

.. confval:: graphics.lightSettings["enable"]
   
   A boolean value activating or deactivating the light config.
   
   By default disabled.

.. todo::
   
   Implement light settings with shader system

Controls
--------

Note that most of these config values are read when the appropriate objects are initialized,
this means that you should consult the objects documentation for how to change the option at runtime.

Mouse
^^^^^

.. confval:: controls.mouse.sensitivity
   
   Degrees to move per pixel traveled by the mouse.
   
   This applies to both horizontal and vertical movement.
   
   Defaults to ``0.15``\ .

Keyboard
^^^^^^^^

.. confval:: controls.controls.movespeed
   
   Speed multiplier for most movements.
   
   Defaults to ``10.0``\ .

.. confval:: controls.controls.verticalspeed
   
   Speed multiplier for vertical movement.
   
   Defaults to ``5.0``\ .

These keys are all registered with the ``mod`` flag set to False, thus they will ignore any modifiers.

.. confval:: controls.controls.forward
             controls.controls.backward
             controls.controls.strafeleft
             controls.controls.straferight
   
   Four basic movement keys.
   
   Each of these keys can be changed individually.
   
   Defaults are ``w``\ , ``s``\ , ``a`` and ``d``\, respectively.

.. confval:: controls.controls.jump
   
   Jump key.
   
   Defaults to ``space``\ .

.. confval:: controls.controls.crouch
   
   Crouch key.
   
   Defaults to ``lshift``\ .

Commonly used Key Combination Configuration Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. confval:: controls.keybinds.common.copy
             controls.keybinds.common.paste
             controls.keybinds.common.cut
   
   Key Combinations used to be used by various parts of the GUI.
   
   Currently used by the :py:class:`peng3d.gui.text.TextInput()` Widget for basic clipboard operations.
   
   By default, these are set to the commonly used values of ``Ctrl-C`` for Copy,
   ``Ctrl-V`` for Paste and ``Ctrl-X`` for Cutting.

General Controls Configuration Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. confval:: controls.keybinds.strict
   
   Whether or not keybindings should be strict.
   
   See :py:class:`peng3d.keybind.KeybindHandler()` for more information.

Debug Options
-------------

All of these options are disabled by default.

.. confval:: controls.keybinds.debug
   
   If enabled, all pressed keybinds will be printed.

.. confval:: debug.events.dump
   
   If enabled, all events are printed including their arguments.
   
   Note that ``on_draw`` and ``on_mouse_motion`` are never printed to avoid excessive outputs.

.. confval:: debug.events.logerr
   
   If enabled, Exceptions catched during event handling are printed.
   
   Note that only :py:exc:`AttributeError` exceptions are catched and printed, other exceptions will propagate further.

.. confval:: debug.events.register
   
   If enabled, all event handler registrations are printed.

.. confval:: debug.events.dumpfile
   
   If not an empty string, this should point to a valid file path for dumping all event names.
   
   If enabled, all event handler registrations and event sends will be logged to this file.
   Note that only the name of the event without data is stored and automatically deduplicated.
   
   Defaults to ``""``\ .

Resource Options
----------------

.. confval:: rsrc.enable
   
   Enables or Disables the resource module.
   
   By default enabled.

.. confval:: rsrc.basepath
   
   Base directory of the Resource Manager.
   
   By default determined via :py:func:`pyglet.resource.get_script_home()`\ .

.. confval:: rsrc.maxtexsize
   
   Maximum Texture size per bin.
   
   Limits the texture in size, useful if the graphics card has big textures (16kx16k) but only few textures will be needed.
   
   By default set to 1024.

.. _cfg-i18n:

Translation Options
-------------------

.. confval:: i18n.enable
   
   Enables or Disables the i18n module.
   
   By default enabled.

.. confval:: i18n.lang
   
   Determines the default language selected upon startup.
   
   Note that setting this config option after creating the first window will have
   no effect. Use :py:meth:`~peng3d.i18n.TranslationManager.setLang()` instead.
   
   Currently defaults to ``en``\ , but may be changed to operating system language
   in the future.

Event Options
-------------

.. confval:: events.removeonerror
   
   If True, automatically removes erroring event handlers.
   Note that the ``raiseErrors`` parameter takes precedent over this setting.
   
   Defaults to ``True``\ .

.. confval:: events.maxignore
   
   An integer number defining the maximum amount of ignored event messages to write to the log file.
   
   This setting is per event, not globally.
   
   Defaults to 3.

Other Options
-------------

.. confval:: pyglet.patch.patch_float2int
   
   Enables the float2int patch for pyglet.
   
   See :py:func:`peng3d.pyglet_patch.patch_float2int()` for more information.
   
   Enabled by default.

.. todo::
   
   Implement more config options
