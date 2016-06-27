
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

.. todo::
   
   Implement fog settings

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

Other Options
-------------

.. todo::
   
   Implement more config options
