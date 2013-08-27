.. installation:

************
Installation
************
This document describes, what is necessary to get the ``spiceminer`` package up
and running. Since it relies on some c-code (of which not all is included in
its source) to be compiled first, that's not as straight forward as one might
hope.

.. preparation:

Preparation
===========
Run ``python getspice.py`` from the project root to automatically download and
unpack the correct version of the c-SPICE source code. If you'd rather do that
manually or have an existing version already available you can simply set an
environment variable named ``CSPICEPATH`` to its path.

After that just use ``python setup.py build`` to build all necessary
extensions.

.. installation:

Installation
============
If building was successfull, just run ``python setup.py install`` and all
should be good to go.
