.. bodies:

******
bodies
******
This module provides a high level data structure, representing entities such as
planets, spacecraft or asteroids.

.. NOTE:: The constructor of :py:class:`~spiceminer.bodies.Body` (and all its
   subclasses) is actually a factory function and the ``type`` of the returned
   entity depends on the provided `body_id`.

.. admonition:: Implementation Detail

   Once created, entities are cached and treated as
   singletons. Because of this, they will not change if the underlying name <-> Id
   mapping is modified at runtime. At the moment there is no API to make changes
   to that mapping, but it's still good to know.

.. automodule:: spiceminer.bodies
   :members:
