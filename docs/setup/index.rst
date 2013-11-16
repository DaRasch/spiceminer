.. _setup:

*****
Setup
*****
This document describes, what is necessary to get the ``spiceminer`` package up
and running. Since it relies on some c-code (of which not all is included in
its source) to be compiled first, that's not as straight forward as one might
hope.

.. _setup-preparation:

Preparation
===========
First get the source from `here <https://github.com/DaRasch/spiceminer>`_, if
you haven't already.

Now run ``python getcspice.py`` from the project root to automatically download
and unpack the correct version of the c-SPICE source code. If you'd rather do
that manually or have an existing version already available you can simply set
an environment variable named ``CSPICEPATH`` to its path.

.. _setup-installation:

Installation
============
There are different ways of installing this package. Each of them has some
advantages and some disadvantages. You should read this, even if you know your
way around installing python packages, because the process can be non-trivial,
especially if you do it by hand.

Direct install
--------------
The easiest solution, but you have little control over it (and possibly not
enough rights).

Just type ``python setup.py install`` and everything will be handled
automatically. If your python installation resides in the systems core
directories (it probably does), you need to prepend the command by
``sudo`` (and of course you need the necessary previleges) on \*NIX machines. To
avoid this trouble, there are some options for the ``install`` command to use
other paths for installation. Type ``python setup.py --help install`` to see
them.

.. NOTE:: The download scripts will not be installed.

If you use `virtualenv <http://www.virtualenv.org>`_, then this is the
recommended way of installing.

Copy-Paste
----------
Very controllable way of installing, but some knowledge about python is
necessary.

Just type ``python setup.py build_ext --inplace`` and the c-extension will be
compiled to ``./spiceminer``. Now you can just copy and paste that directory
wherever you want.

This of course dosn't mean, that python will automatically find the package. To
ensure, that python is always able to find it, you need to manipulate your
``PYTHONPATH`` accordingly.

.. _setup-verification:

Verification (optional)
=======================
To guarantee, that the version you grabbed is fully functional and compiled
correctly, you may run some tests on it.

For this it is required to have the base spice-data at
hand. The ``getdata.py`` script will download those for you. Just use
``python getdata.py base`` to download all necessary data directly to the
spiceminer root directory.

.. NOTE:: See the :ref:`tutorial <tutorial-getting-started>` for more info on
   what ``getdata.py`` can do.

If you have already obtained those yourself, and/or they are located in a
different directory, you should set an environment variable named
``SPICEMINERDATA`` to that path.
Alternatively you can just symlink that folder into the spiceminer root folder
under the name *data*.

Now run ``python setup.py test``. If it reports no errors, continue.
Otherwise something went wrong. In that case best file a bug report.
