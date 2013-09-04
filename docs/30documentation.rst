.. _documentation:

*************
Documentation
*************

.. _documentation-import-all:

Import \*
=========

By default the ``spiceminer`` package exports the following functions, classes
and modules:

- :py:mod:`~spiceminer.kernel` -- Access to the database.
- :py:class:`~spiceminer.time_.Time` -- Powerfull implementation of POSIX time.
- :py:func:`~spiceminer._helpers.frange` -- ``xrange()`` for ``float``.
- :py:func:`~spiceminer._helpers.dtrange` -- ``xrange()`` for ``datetime``.

To fully utilize the power of this package, you should of course also know
about the abstraction used for the spice data.
The :py:class:`~spiceminer.bodies.Body`.

.. _documentation-modules:

Modules in detail
=====================

.. toctree::
   :maxdepth: 2

   31kernel
   32bodies
   33time_
   35helpers
