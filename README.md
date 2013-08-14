spiceminer
==========

What is it?
-----------
This module is a high level python wrapper around the spice c-library provided by NASA to store and analyse operational data from several space missions. It concentrates on an easy to use API for analysing the data.

Installation:
-------------
To get things working you need to have numpy and spice (a low level python wrapper around the spice c-API that can be found at https://github.com/rca/PySPICE) in your PYTHONPATH

Building:

  Download the spice sources for your OS here: http://naif.jpl.nasa.gov/naif/toolkit_C.html

  Export its root directory as an environment variable called ```CSPICEPATH```. Alternatively you can just drop the spice root in the root of spiceminer.
  To build the c-libraries, simply run ```python setup.py build```

Installing:
  After building, just run ```python setup.py install``` and all should be good to go.

Usage:
------
See example.py



Other stuff:
------------
Import hierarchy:
```
    +------------+
    | spiceminer |----------+
    +------------+          |
        |      |            |
    +--------+ |            |
  +-| kernel |--------------+
  | +--------+ |            |
  |     |      |            |
  | +--------+ |            |
  +-| bodies |--------------+
  | +--------+ |            |
  |     |      |            |
  | +------+   |      +----------+
  +-| time |---+      | _helpers |
  | +------+          +----------+
  |
+---------------+
| _spicewrapper |
+---------------+
```
