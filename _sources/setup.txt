Setup
*****

Getting the source
==================
The source code for the spiceminer package can be downloaded from
`here <https://github.com/DaRasch/spiceminer>`_.

Quickstart
==========
In most cases these steps should be sufficient for a new install:

1) ``python setup.py cspice``
2) ``python setup.py build_ext --inplace``
3) ``python setup.py data``

Getting CSPICE
==============
The spiceminer package requires some external C-code to work. This code can be
downloaded from `here <https://naif.jpl.nasa.gov/naif/toolkit_C.html>`_, or by
running ``python setup.py cspice`` from inside the spiceminer project directory.
This script will automatically check your system and download the version best
suited for your system.

If you download the the code yourself there are 2 different ways to make sure it
is available in the build process:

1) Copy or symlink the unzipped code to *spiceminer/cspice*.

2) Set the environment variable ``CSPICEPATH`` to the absolute path of the
   unzipped code.

Building
========
To compile the C-extension run ``python setup.py build_ext --inplace``. This
will generate the C-library and put it in the correct directory. You can now
copy the *spiceminer/spiceminer* folder to somewhere on your ``PYTHONPATH``.

.. NOTE:: If you use the standard ``setup.py install`` method of installing you
 don't need to do this as it will automatically be done while installing.

Getting data
============
NASA hosts a lot of kernels `here <https://naif.jpl.nasa.gov/naif/data.html>`_.

spiceminer also comes with a little script that can automatically download some
kernel collections for you. Currently available collections are:

base
    Information about planets and moons from Mercury to Mars.
    Also includes a leapseconds kernel that is necessary to use any position/
    rotation information at all.
msl
    Information about the Mars Science Laboratory and its rover.
helios
    Information about the helios mission.
ulysses
    Information about the ulysses mission.

To download any of these, simply call
``python setup.py data options=[name[,name...]]`` from the project directory.
