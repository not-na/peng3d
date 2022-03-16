Quickstart
==========

In this guide, we will learn how to create a simple GUI using ``peng3d``\ .

.. seealso::
   For a more complex example, see :doc:`3d-app/index`\ .

Basic Structure
---------------

In this guide, we will be writing our app using only a single Python file for simplicity.
For more complex projects, it is recommended to split your application by menus or even submenus
into different files.

First, here's the minimum example required to show anything with ``peng3d``::

   import peng3d

   peng = peng3d.Peng()

   peng.createWindow(caption="Hello World!", resizable=True)

   main_menu = peng3d.Menu("main", peng.window, peng)
   peng.window.addMenu(main_menu)

   peng.window.changeMenu("main")
   peng.run()

If you run the app now, you should see a black window with a title of ``Hello World!``\ :

.. image:: quickstart_black_window.png

While most of the lines should be fairly self-explanatory, let's go through them one by one.

First, we start by importing ``peng3d`` and creating an instance of the :py:class:`peng3d.Peng()` class::

   import peng3d

   peng = peng3d.Peng()

There should only be one instance of this class per app, shared between all components.
It manages the event system and some other globally shared resources.

Next, we create our window with the desired caption::

   peng.createWindow(caption="Hello World!", resizable=True)

Since we want to keep this example very simple, we only pass a caption and activate resizing.
All arguments to :py:meth:`Peng.createWindow()` are optional and should be passed as keyword
arguments. Any arguments not recognized by ``peng3d`` are passed through to the underlying
:py:class:`PengWindow` class, which will in turn pass through unrecognized arguments to
``pyglet``\ .

.. seealso::
   See the :py:mod:`pyglet.window` module docs for a list of all arguments.

Now that we have created our window, we'll create our first menu and register it::

   main_menu = peng3d.Menu("main", peng.window, peng)
   peng.window.addMenu(main_menu)

The basic :py:class:`Menu` class is designed for layer-based rendering. We will later change
this, since we want to create a GUI with widgets.

Also, we always need to register menus (and later also submenus and widgets), so it is a
good practice to always register a menu right after creating it.

Lastly, we'll switch to our main menu and start the application::

   peng.window.changeMenu("main")
   peng.run()

The call to :py:meth:`changeMenu()` can be used to switch between different menus, here
we use it to define which menu our app starts with. Note that we pass in the name of our menu,
not the menu object itself.

The final call to ``peng.run()`` starts the internal event loop of pyglet and blocks until
the application exits, usually by clicking the X button.

.. note::
   The code described in this subsection can also be found in ``examples/quickstart_basic.py`` `here <https://github.com/not-na/peng3d/tree/master/quickstart_basic.py>`_\ .

Creating our first widget
-------------------------

.. todo::
   Write this subsection

Switching between menus
-----------------------

.. todo::
   Write this subsection

Dynamically adjusting our layout to the window size
---------------------------------------------------

.. todo::
   Write this subsection

Further reading
---------------

There are other, more advanced guides available. For example, take a look at :doc:`3d-app/index`\ .

.. seealso::
   See the ``examples/`` folder on the `main repository <https://github.com/not-na/peng3d/tree/master/examples>`_
   for more examples of various ``peng3d`` features.