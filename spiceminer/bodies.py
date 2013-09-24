#-*- coding:utf-8 -*-

import collections
import numbers
import numpy

import spiceminer._spicewrapper as spice

from spiceminer.time_ import Time
from spiceminer._helpers import ignored

__all__ = ['Body', 'Asteroid', 'Barycenter', 'Comet', 'Instrument', 'Planet',
           'Satellite', 'Spacecraft']


### Helper ###
def _iterbodies(start, stop, step=1):
    for i in xrange(start, stop, step):
        with ignored(ValueError):
            yield Body(i)


class Body(object):
    '''Base class for representing ephimeres objects.

    :type body_id: ``int``
    :arg body_id: ID of the ephimeris object referenced by ``body_id``.
    :return: (``Body``) -- Representation of the requested entity.
    :raises:
      (``ValueError``) -- If the provided ``body_id`` does not reference
      any entity.

      (``TypeError``) -- If the provided ``body_id`` is not of type ``int``.
    '''

    _CACHE = {}
    _ABCORR = 'NONE'

    def __new__(cls, body_id, *args, **kwargs):
        if not isinstance(body_id, numbers.Integral):
            msg = 'Body() integer argument expected, got {}.'
            raise TypeError(msg.format(type(body_id)))
        ### factory function ###
        if body_id in Body._CACHE:
            body = Body._CACHE[body_id]
        elif body_id > 2000000:
            body = object.__new__(Asteroid, body_id, *args, **kwargs)
        elif body_id > 1000000:
            body = object.__new__(Comet, body_id, *args, **kwargs)
        elif body_id > 1000:
            body = object.__new__(cls, body_id, *args, **kwargs)
        elif body_id > 10:
            if body_id % 100 == 99:
                body = object.__new__(Planet, body_id, *args, **kwargs)
            else:
                body = object.__new__(Satellite, body_id, *args, **kwargs)
        elif body_id == 10:
        #    body = object.__new__(cls, 10, *args, **kwargs)
            body = object.__new__(Planet, body_id, *args, **kwargs)
        elif body_id >= 0:
            body = object.__new__(Barycenter, body_id, *args, **kwargs)
        elif body_id > -1000:
            body = object.__new__(Spacecraft, body_id, *args, **kwargs)
        elif body_id >= -100000:
            body = object.__new__(Instrument, body_id, *args, **kwargs)
        else:
            body = object.__new__(Spacecraft, body_id, *args, **kwargs)
        return body

    def __init__(self, body_id):
        self._id = body_id
        self._name = spice.bodc2n(body_id)
        self._frame = None
        if self._name is None:
            msg = 'Body() {} is not a valid ID.'
            raise ValueError(msg.format(body_id))
        Body._CACHE[body_id] = self

    def __str__(self):
        return self.__class__.__name__ + ' {} (ID {})'.format(self.name, self.id)

    def __repr__(self):
        return self.__class__.__name__ + '({})'.format(self.id)

    @property
    def id(self):
        '''The ID of this object.'''
        return self._id
    @property
    def name(self):
        '''The name of this object.'''
        return self._name

    def parent(self):
        '''Get object, this :py:class:`~spiceminer.bodies.Body` is bound to (be
            it orbiting or physical attachment).
        '''
        return None

    def children(self):
        '''Get objects bound to this :py:class:`~spiceminer.bodies.Body`.
        '''
        return []

    def state(self, times, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        '''Get the position and speed of this object relative to the observer
        in a specific reference frame.

        :type times: ``Iterable`` | has ``__float__()``
        :arg times: The point(s) in time for which to calculate the
          position/speed.

        :type observer: :py:class:`~spiceminer.bodies.Body` | ``str``
        :arg observer: Object to use as (0,0,0).

        :type abcorr: ``str``
        :arg abcorr: Aberration correction to be applied. May be one of LT,
          LT+S, CN, CN+S, XLT, XLT+S, XCN, XCN+S. For explanation of these see
          `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        :return: (``ndarray``) -- The nx7 array containing time and
          (x, y, z)-position/speed.
        :raises:
          (``TypeError``) -- If an argument doesn't conform to the type
          requirements.

          (:py:class:`~spiceminer._spicewrapper.SpiceError`) -- If there is
          necessary information missing.
        '''
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            result = []
            for time in times:
                with ignored(spice.SpiceError):
                    data = spice.spkezr(self.name, Time.fromposix(time).et(),
                        frame, abcorr or Body._ABCORR, observer)
                    result.append([time] + data[0] + [data[1]])
            return numpy.array(result).transpose()
        msg = 'state() Real or Iterable argument expected, got {}.'
        raise TypeError(msg.format(type(times)))

    def single_state(self, time, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkezr(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer))

    def position(self, times, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        '''Get the position of this object relative to the observer in a
        specific reference frame.

        :type times: ``Iterable`` | has ``__float__()``
        :arg times: The point(s) in time for which to calculate the position.

        :type observer: :py:class:`~spiceminer.bodies.Body` | ``str``
        :arg observer: Object to use as (0,0,0).

        :type abcorr: ``str``
        :arg abcorr: Aberration correction to be applied. May be one of LT,
          LT+S, CN, CN+S, XLT, XLT+S, XCN, XCN+S. For explanation of these see
          `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        :return: (``ndarray``) -- The nx4 array containing time and
          (x, y, z)-position.
        :raises:
          (``TypeError``) -- If an argument doesn't conform to the type
          requirements.

          (:py:class:`~spiceminer._spicewrapper.SpiceError`) -- If there is
          necessary information missing.
        '''
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            result = []
            for time in times:
                with ignored(spice.SpiceError):
                    result.append([time] + spice.spkpos(self.name,
                    Time.fromposix(time).et(), frame, abcorr or Body._ABCORR,
                    observer)[0])
            return numpy.array(result).transpose()
        msg = 'position() Real or Iterable argument expected, got {}.'
        raise TypeError(msg.format(type(times)))

    def single_position(self, time, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkpos(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer)[0])

    def speed(self, times, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        '''Get the speed of this object relative to the observer in a specific
        reference frame.

        :type times: ``Iterable`` | has ``__float__()``
        :arg times: The point(s) in time for which to calculate the speed.

        :type observer: :py:class:`~spiceminer.bodies.Body` | ``str``
        :arg observer: Object relative to which movement happens.

        :type abcorr: ``str``
        :arg abcorr: Aberration correction to be applied. May be one of LT,
          LT+S, CN, CN+S, XLT, XLT+S, XCN, XCN+S. For explanation of these see
          `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        :return: (``ndarray``) -- The nx4 array containing time and
          (x, y, z)-speed.
        :raises:
          (``TypeError``) -- If an argument doesn't conform to the type
          requirements.

          (:py:class:`~spiceminer._spicewrapper.SpiceError`) -- If there is
          necessary information missing.
        '''
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            data = self.state(times, observer, frame, abcorr)
            return data[numpy.array([True] + [False] * 3 + [True] * 3)]
        msg = 'speed() Real or Iterable argument expected, got {}.'
        raise TypeError(msg.format(type(times)))

    def single_speed(self, time, observer='SUN', frame='ECLIPJ2000', abcorr=None):
        return self.single_state(time, observer, frame, abcorr)[3:]

    def rotation(self, times, observer='ECLIPJ2000'):
        '''Get the rotation matrix for rotating this object from its own
        reference frame to that of the observer.

        :type times: ``Iterable`` | has ``__float__()``
        :arg times: The point(s) in time for which to calculate rotations.

        :type observer: :py:class:`~spiceminer.bodies.Body` | ``str``
        :arg observer: Object/reference frame to transform to.

        :return: (``list``) -- The list of 3x3 rotation matrizes.
        :raises:
          (``TypeError``) -- If an argument doesn't conform to the type
          requirements.

          (:py:class:`~spiceminer._spicewrapper.SpiceError`) -- If there is
          necessary information missing.
        '''
        if isinstance(observer, Body):
            observer = observer._frame or observer.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            result = []
            valid_times = []
            for time in times:
                with ignored(spice.SpiceError):
                    result.append(spice.pxform(self._frame or self.name,
                        observer, Time.fromposix(time).et()))
                    valid_times.append(time)
            return numpy.array(valid_times), [numpy.array(item).reshape(3, 3)
                for item in result]
        msg = 'rotation() Real or Iterable argument expected, got {}.'
        raise TypeError(msg.format(type(times)))

    def single_rotation(self, time, destination='ECLIPJ2000'):
        if isinstance(destination, Body):
            destination = detination._frame or destination.name
        return numpy.array(spice.pxform(self._frame or self.name, destination,
            Time.fromposix(time).et())).reshape(3, 3)


class Asteroid(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing asteroids.

    Asteroids are ephimeris objects with IDs > 200000.
    '''
    def __init__(self, body_id):
        super(Asteroid, self).__init__(body_id)


class Barycenter(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing a
    barycenter of an ephimeris object and all of its satellites.

    Barycenters are ephimeris objects with IDs between 0 and 9.
    '''
    def __init__(self, body_id):
        super(Barycenter, self).__init__(body_id)


class Comet(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing comets.

    Comets are ephimeris objects with IDs between 100000 and 200000.
    '''
    def __init__(self, body_id):
        super(Comet, self).__init__(body_id)


class Instrument(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing instruments
    mounted on spacecraft (including rovers and their instruments).

    Instruments are ephimeris objects with IDs between -1001 and -10000.
    '''
    def __init__(self, body_id):
        super(Instrument, self).__init__(body_id)

    def parent(self):
        offset = 0 if self.id % 1000 == 0 else -1
        spacecraft_id = self.id / 1000 + offset
        return Body(spacecraft_id)


class Planet(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing planets.

    Planets are ephimeris objects with IDs between 199 and 999 with
    pattern [1-9]99.
    '''
    def __init__(self, body_id):
        super(Planet, self).__init__(body_id)
        self._frame = 'IAU_' + self._name

    def parent(self):
        return Body(10)

    def children(self):
        return list(_iterbodies(self.id - 98, self.id))


class Satellite(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing satellites
    (natural bodies orbiting a planet).

    Satellites are ephimeris objects with IDs between 101 and 998 with
    pattern [1-9][0-9][1-8].
    '''
    def __init__(self, body_id):
        super(Satellite, self).__init__(body_id)

    def parent(self):
        return Body(self.id - self.id % 100 + 99)


class Spacecraft(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing spacecraft.

    Spacecraft are ephimeris objects with IDs between -1 and -999 or < -99999.
    '''
    def __init__(self, body_id):
        super(Spacecraft, self).__init__(body_id)

    def children(self):
        return list(_iterbodies(self.id * 1000, self.id * 1000 - 1000, -1))
