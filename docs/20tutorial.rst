.. _tutorial:

********
Tutorial
********
Here I will show you the basics of how spiceminer works.


.. _tutorial-getting-started:

Getting started
===============
Before we start actually mining data, we need to actually download some data.
for this we will use the ``getdata.py`` script that ships with spiceminer.

First lets get the files that are most important. These are:
* A leapseconds kernel for time conversion.
* Kernels containing the position of the sun, planets and their natural satellites.
* Kernels containing the rotation of the sun, planets and their natural satellites.

To get those files we type ``python getdata.py base``. This will copy all
necessary files to the directory ``data/base`` relative to the folder in which
the script is located. If you want to use a different directory as base, just
add the option ``--dir <path>``. To update these files you can do the same
again. It will only download new/out of date files to minimize bandwidth and
time consumption.

If that is all the data you need, you can proceed to the
:ref:`next chapter <tutorial-loading-kernels>`, but if you want some mission
data as well, then stay with me.

As of writing the missions supported are *MSL*, *HELIOS* and *ULYSSES*.To see
all currently available missions as well as other command line options, type
``python getdata.py -h``. Other missions must be downloaded by hand. You can
find a list of available data on the official
`NAIF website <http://naif.jpl.nasa.gov/naif/data_operational.html>`_. Please
make sure to read the readme for your mission of interest to find out about
the necessary kernels.


.. _tutorial-loading-kernels:

Loading kernels
===============
We will from now on assume that we work under Linux and all necessary data are
stored under ``/home/user/data``.

Now, if we ``cd ~/data`` and start a python interpreter we most likely just
need to do the following::

    >>> from spiceminer import *
    >>> kernel.load()
    29

The number returned by ``kernel.load()`` is the number of documents scanned.

If we don't want to change the working directory just to load the data, we can
just feed the path to the loading function like so::

    >>> from spiceminer import *
    >>> kernel.load('/home/user/data')
    29
    >>> kernel.load('data') # If we are at /home/user
    29

As you can see, both relative and absolute paths work.

| Ok that's all cool and stuff but what happens if there are kernels in
  ``data/base`` and ``data/msl`` for example and i wnt ro load all of them?
| Actually that is the standart behaviour of the function. It loads all kernels
  in a given directory tree recursively starting at the root.

| Fine, but how about I only want to load ``data`` but not ``data/base`` or
  ``data/msl``?
| First off, this won't be necessary in most cases, since loading kernels is
  quite fast. But if you really want to, you can do this:

::

    >>> from spiceminer import *
    >>> kernel.load('data', recursive=False)
    0

Another thing that might happen, is that you have symlinks to directories in
the directory tree. by default those are ignored to avoid possible infinite
recursion. If you know what you are doing you can turn this protection off by
passing the *followlinks* parameter like so::

    >>> from spiceminer import *
    >>> kernel.load('data', folowlinks=True)
    29

You can also unload kerenls again if they are no longer needed::

    >>> from spiceminer import *
    >>> kernel.load('data')
    29
    >>> kernel.unload('data')
    29

This is not requiered. The kernels will automatically be unloaded, once the
session is closed or the programm finishes.


.. _tutorial-ephimeris-objects:

Ephimeris objects
=================
Once you have loaded the kernels you need, it's time to use them. Every
physical object defined by a kernel is represented by a subclass of
:py:class:`~spiceminer.bodies.Body` instance. Getting hold of them is pretty
easy::

    >>> from spiceminer import *
    >>> kernel.get('EARTH')
    Planet(399)

As you can see, the return value is pretty descriptive. It tells us what kind
of :py:class:`~spiceminer.bodies.Body` we got and what its reference number
is.

You might wonder why this works, since we haven't loaded any kernels. It is due
to the fact, that some Objects are hardcoded into the framework. This is the
case for the sun, all planets and their natural satellites, and all spacecraft.

We can already extract information from this object, just not position or
rotation. Those are only available through kernels. Some info we can get about
it::

    >>> from spiceminer import *
    >>> earth = kernel.get('EARTH')
    >>> earth.name
    'EARTH'
    >>> earth.id
    399
    >>> earth.parent()
    Planet(10)
    >>> earth.parent().name
    'SUN'
    >>> earth.children()
    [Satellite(301)]
    >>> earth.children()[0].name
    'MOON'
    print EARTH
    Planet EARTH (ID 399)


.. _tutorial-getting-data:

Getting data
============
Now for the interesting part. If the appropriate kernels are loaded, you can
extract position, speed and rotation data from them. A simple example::

    >>> from spiceminer import *
    >>> kernel.load('data')
    29
    >>> t = frange(Time(2013), Time(2014), Time.DAY) # Make a time span
    >>> earth = kernel.get('EARTH')
    >>> earth.position(t)
    array([[  1.35699840e+09,   1.35708480e+09,   1.35717120e+09, ...,
              1.38827520e+09,   1.38836160e+09,   1.38844800e+09],
           [ -2.69289918e+07,  -2.94962808e+07,  -3.20546002e+07, ...,
             -1.85068538e+07,  -2.10999869e+07,  -2.36866752e+07],
           [  1.44612884e+08,   1.44110525e+08,   1.43563419e+08, ...,
              1.45947604e+08,   1.45592016e+08,   1.45190880e+08],
           [ -3.95472912e+03,  -3.94411592e+03,  -3.95337411e+03, ...,
             -4.59965922e+03,  -4.67683468e+03,  -4.74105184e+03]])

Here we got the x,y,z coordinates of the earth relative to the sun using the
*ECLIPJ2000* reference frame over the time of 1 year. The format of the
returned array is::

     array([[time,    time,    time,    time,    time,    time,    time,    time]
            [x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos]
            [y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos]
            [z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos]])




.. _tutorial-advanced-examples:

Advanced examples
=================
Measure the angular disposition of the mars rover curiosity::

    >>> from spiceminer import *
    >>> import numpy as np
    >>> # First define the angle function:
    >>> def angle(v0, v1):
    ...     v0, v1 = v0.T[0], v1.T[0]
    ...     unit_v0 = v0 / np.sqrt(np.dot(v0, v0))
    ...     unit_v1 = v1 / np.sqrt(np.dot(v1, v1))
    ...     return np.arccos(np.dot(unit_v0, unit_v1))
    ...
    >>> kernel.load('data')
    29
    >>> t = list(frange(Time(2012,10), Time(2013, 3), Time.HOUR))
    >>> z = np.array([[0],[0],[1]])
    >>> mars = kernel.get('MARS')
    >>> rover = kernel.get('MSL_ROVER')
    >>> pos = rover.position(t, mars, mars)
    >>> rot = rover.rotation(t, mars)
    >>> rad = np.array([angle(r.dot(-z), pos[1:, i].reshape(3,1)) for i, r in enumerate(rot)])
    >>> array(rad)
    array([ 0.07098081,  0.07098081,  0.07098081, ...,  0.08967051,
            0.08967051,  0.08967051])


