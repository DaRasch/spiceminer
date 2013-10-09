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

After that just use ``python setup.py build`` to build all necessary
extensions.

.. _setup-verification:

Verification
============
To guarantee, that the version you grabbed is fully functional and compiled
correctly, you should run the test suite. It is not required, but strongly
recommended.

For that it is required to have at least the the newest base spice-data at
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

.. _setup-installation:

Installation
============
If building and verification were successfull, just run
``python setup.py install`` and all should be good to go. If you are not
working with `virtualenv <http://www.virtualenv.org>`_ you may need to prepend
``sudo`` on unix machines.

If you don't want to install the package automatically, but want to copy it
manually later on, you can susbstitute the ``python setup.py build`` step for
``python build_ext --inplace`` to generate the c-library directly inside the
source code directory.

.. NOTE:: The download scripts will not be installed.
