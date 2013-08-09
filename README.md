spiceminer
==========

What is it?
-----------
This module is a high level python wrapper around the spice c-library provided by NASA to store and analyse operational data from several space missions. It concentrates on an easy to use API for analysing the data.

Installation:
-------------
To get things working you need to have numpy and another project in your PYTHONPATH:
https://github.com/rca/PySPICE
This is a low level wrapper around the spice c-API and currently used for most functions.

Building: (NOT relevant yet)
  Download the spice sources for your OS here: http://naif.jpl.nasa.gov/naif/toolkit_C.html
  Export its root directory as an environment variable called ```CSPICEPATH```. Alternatively you can just drop the spice root in the root of spiceminer.
  To build the c-libraries, simply run ```python setup.py build```

Installing:
  Just run ```python setup.py install``` and all should be good to go.

Usage:
------
See example.py




Import hierarchy:
```
+------------+
| spiceminer |----------+
+------------+          |
    |      |            |
+--------+ |            |
| kernel |--------------+
+--------+ |            |
    |       \           |
+---------+ |           |
| _bodies |-------------+
+---------+ |           |
    |       |           |
+-------+   |     +----------+
| _time |---+     | _helpers |
+-------+         +----------+
```
