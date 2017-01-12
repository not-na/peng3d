
``peng3d`` - Peng3D main module
===============================

.. py:module:: peng3d
   :synopsis: Peng3D main module

This Module represents the root of the peng3d Engine.

Most classes contained in submodules are available under the same name, e.g. you can use :py:class:`peng3d.Peng()` instead of :py:class:`peng3d.peng.Peng()`\ .
Note that for compatibility reasons, peng3d.window is not available by default and will need to be imported directly.

``*``\ - importing submodules should be safe as most modules define an ``__all__`` variable.

.. toctree::
   :maxdepth: 1
   
   peng3d.peng
   peng3d.window
   peng3d.layer
   peng3d.menu
   gui/index
   gui/widgets
   gui/button
   gui/text
   gui/container
   gui/slider
   peng3d.resource
   peng3d.model
   peng3d.camera
   peng3d.world
   actor/index
   actor/player
   peng3d.keybind
   peng3d.config
   peng3d.pyglet_patch
   peng3d.version
