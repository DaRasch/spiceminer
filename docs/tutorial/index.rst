.. _tutorial:

********
Tutorial
********
Here I will show you the basics of how spiceminer works.


.. _tutorial-getting-started:

Getting started
===============
Before we start actually mining data, we need to download some data. For this
we will use the ``getdata.py`` script that ships with spiceminer.

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
data as well, then read on.

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
stored under ``/home/<user>/data``.

Now, if we ``cd ~/data`` and start a python interpreter we most likely just
need to do the following::

    >>> from spiceminer import *
    >>> kernel.load()
    22

The number returned by ``kernel.load()`` is the number of kernels loaded.

If we don't want to change the working directory just to load the data, we can
feed the path to the loading function like so::

    >>> from spiceminer import *
    >>> kernel.load('/home/user/data')
    22
    >>> kernel.load('data') # If we are at /home/user
    22

As you can see, both relative and absolute paths work.

| Ok that's all cool and stuff but what happens if there are kernels in
  ``data/base`` and ``data/msl`` for example and i want ro load all of them?
| Actually that is the standart behaviour of the function. It loads all kernels
  in a given directory tree recursively starting at the root.

| Fine, but how about I only want to load ``data`` but not ``data/base`` or
  ``data/msl``?
| First off, this won't be necessary in most cases, since loading kernels is
  quite fast. But if you really want to, you can do this:

::

    >>> from spiceminer import *
    >>> kernel.load('data', recursive=False)
    5

Another thing that might happen, is that you have symlinks to other directories
in the directory tree. By default those are ignored to avoid possible infinite
recursions. If you know what you are doing you can turn this protection off by
passing the *followlinks* parameter like so::

    >>> from spiceminer import *
    >>> kernel.load('data', folowlinks=True)
    29

You can also unload kernels again if they are no longer needed::

    >>> from spiceminer import *
    >>> kernel.load('data')
    22
    >>> kernel.unload('data')
    22

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

.. NOTE:: The input of :py:func:`~spiceminer.kernel.get` is **not** case
   sensitive. I just wrote *EARTH* in all caps, because that is the standart
   convention of the spice-API.

You might wonder why this works, since we haven't loaded any kernels. It is due
to the fact, that some Objects are hardcoded into the framework. This is the
case for the sun, all planets and their natural satellites, and all spacecraft.

We can already extract information from this object, just not position or
rotation, those are only available through kernels. Some info we can get about
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


.. _tutorial-excursus:

Excursus: Time, frange and others
=================================
With this package come some functions/classes, which are not necessary, but
are very usefull.


.. _tutorial-excursus-time:

A good time representation
--------------------------
To extract rotation and position information from an Ephimeris Object, we need
to specify the time, for which we want that information. By convention, all
methods in need of time information, take those as (iterables of) integers
representing POSIX time (seconds since 1970-01-01T00:00:00). The
:py:class:`~spiceminer.time_.Time` class allows easy handling of those times,
because internally it is just an integer, but at the same time it exposes most
of the ``datetime`` interface and some other neat features.

The easiest way of creating an instance of :py:class:`~spiceminer.time_.Time`::

    >>> from spiceminer import *
    >>> epoch = Time(2000, hour=12)
    >>> print epoch
    2012-01-01T12:00:00.0

As you can see, it is possible to omit parameters. Omitted parameters will
default to their respective value at 1970-01-01T00:00:00.

We can also instatiate :py:class:`~spiceminer.time_.Time` from POSIX time or
even ``datetime``::

    >>> from spiceminer import *
    >>> from datetime import datetime
    >>> dt = datetime(2000, 1, 1, 12)
    >>> print Time.fromdatetime(dt)
    2012-01-01T12:00:00.0
    >>> print Time.fromposix(1325419200)
    2012-01-01T12:00:00.0
    >>> print Time.fromydoy(2012, 0.5)
    2012-01-01T12:00:00.0

As mentioned above, all time dependant methods accept iterables. We could use
the builtin ``range`` like this::

    >>> from spiceminer import *
    >>> start = Time(2000, hour=12)
    >>> stop = Time(2000, 6, hour=12)
    >>> step = Time.DAY
    >>> range(int(start), int(stop), int(step))
    [1325419200, 1325505600, 1325592000, ...]

But that is somewhat ugly and limeted to integers, while
:py:class:`~spiceminer.time_.Time` can represent fractions of a second.
Fortunately, that can be fixed.


.. _tutorial-excursus-frange:

range for floats
----------------
The :py:class:`~spiceminer.extra.frange` function behaves just like the builtin
``xrange``, but can handle floats. It allows for much easier (and more memory
friendly) :py:class:`~spiceminer.time_.Time`-iterables::

    >>> from spiceminer import *
    >>> start = Time(2000, hour=12)
    >>> stop = Time(2000, 6, hour=12)
    >>> step = Time.DAY
    >>> frange(start, stop, step)
    <generator object _range at 0x258d170>

The result looks a little strange, but if you are familiar with iterators, you
know why. If not, think of it like a list that can only be iterated over once
and not be indexed.


.. _tutorial-getting-data:

Getting data
============
Now for the interesting part. If the appropriate kernels are loaded, you can
extract position, speed and rotation data from them. A simple example::

    >>> from spiceminer import *
    >>> kernel.load('data')
    22
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

We can of course change the reference Frame and the observer. For example, we
can check the position of the Curiosity rover on the Mars surface::

    >>> from spiceminer import *
    >>> kernel.load('data')
    22
    >>> t = frange(Time(2012), Time(2012, 6), Time.DAY)
    >>> mars = kernel.get('mars')
    >>> msl_rover = kernel.get('msl_rover')
    >>> msl_rover.position(t, observer=mars, frame=mars)
    array(...)




.. _tutorial-advanced-examples:

Advanced examples
=================
Measure the angular tilt of the mars rover curiosity relative to its position
on Mars::

    >>> from spiceminer import *
    >>> import numpy as np
    >>> kernel.load('data')
    22
    >>> t = list(frange(Time(2012,10), Time(2013, 3), Time.HOUR))
    >>> z = np.array([0, 0, 1])
    >>> mars = kernel.get('MARS')
    >>> rover = kernel.get('MSL_ROVER')
    >>> pos = rover.position(t, mars, mars)
    >>> rot = rover.rotation(t, mars)
    >>> rad = np.array([angle(r.dot(-z), pos[1:, i]) for i, r in enumerate(rot)])
    >>> rad
    array([ 0.07098081,  0.07098081,  0.07098081, ...,  0.08967051,
            0.08967051,  0.08967051])


