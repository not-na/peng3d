Installation
============

There are several different ways to install ``peng3d``. The most common ways are listed below.

Using ``pip``
-------------

This is by far the simplest way to install ``peng3d``. Simply run the following command::

   $ pip install peng3d

You may also wish to add ``peng3d`` to your ``requirements.txt`` or similar file.

.. seealso::
   See the documentation of the `Requirements File Format <https://pip.pypa.io/en/stable/reference/requirements-file-format/>`_
   for more details regarding dependency specification.


From source
-----------

If you wish to install a development version that is not available on PyPI, you can also
install ``peng3d`` directly from its source code.

First, you'll have to download the code somewhere. This can be done in any way you like,
but here is how it can be done using ``git``::

   $ git clone https://github.com/not-na/peng3d.git
   $ cd peng3d

After having downloaded the source code, you can now install it using the ``setup.py`` file::

   $ python setup.py install

If there weren't any errors, ``peng3d`` should now be installed.

Where to go next
----------------

After having installed ``peng3d``\ , you may wish to look at the :doc:`quickstart` Guide for
a simple and fast introduction to ``peng3d`` or the :doc:`3d-app/index` Guide for a more
in-depth guide.

There are also some examples available in the ``examples/`` folder on the `main repository <https://github.com/not-na/peng3d/tree/master/examples>`_\ .