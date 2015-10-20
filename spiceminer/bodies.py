#-*- coding:utf-8 -*-

import collections
import numbers
import numpy

from . import _spicewrapper as spice

from .time_ import Time
from ._helpers import ignored
from .kernel.highlevel import Kernel

__all__ = ['get', 'Body', 'Asteroid', 'Barycenter', 'Comet', 'Instrument',
            'Planet', 'Satellite', 'Spacecraft', 'Star']


### Helpers ###
def _iterbodies(start, stop, step=1):
    for i in xrange(start, stop, step):
        with ignored(ValueError):
            yield Body(i)

### Public API ###
def get(body):
    '''Get body by name or id.

    Parameters
    ----------
    body: str|int|Body
        The name or id of the requested body.

    Returns
    -------
    Body
        A representation of the requested body.

    Raises
    ------
    ValueError
        If the provided name/ID doesn't reference a loaded body.
    TypeError
        If `body` has the wrong type.
    '''
    return Body(body)


class Body(object):
    '''Base class for representing ephimeres objects.

    Parameters
    ----------
    body: str|int|Body
        The name or ID of the requested body.

    Raises
    ------
    ValueError
        If the provided name/ID doesn't reference a loaded body.
    TypeError
        If `body` has the wrong type.
    '''

    _ABCORR = 'NONE'

    #TODO: implement Body.LOADED

    def __new__(cls, body, *args, **kwargs):
        # Check and convert type
        if isinstance(body, Body):
            body = Body(body.id)
        elif isinstance(body, basestring):
            num = spice.bodn2c(body)
            if num is None:
                raise ValueError("Got invalid name '{}'".format(body))
            body = num
        elif not isinstance(body, int):
            msg = "'int' or 'str' argument expected, got '{}'"
            raise TypeError(msg.format(type(body)))
        if body not in set.union(set(), *(k.ids for k in Kernel.LOADED)):
            # TODO: Change to Body.LOADED when implemented
            msg = "No loaded 'Body' with ID or name '{}'"
            raise ValueError(msg.format(body))
        # Create correct subclass
        # XXX: move to metaclass?
        elif body > 2000000:
            body = object.__new__(Asteroid, body, *args, **kwargs)
        elif body > 1000000:
            body = object.__new__(Comet, body, *args, **kwargs)
        elif body > 1000:
            body = object.__new__(cls, body, *args, **kwargs)
        elif body > 10:
            if body % 100 == 99:
                body = object.__new__(Planet, body, *args, **kwargs)
            else:
                body = object.__new__(Satellite, body, *args, **kwargs)
        elif body == 10:
            body = object.__new__(Star, body, *args, **kwargs)
        elif body >= 0:
            body = object.__new__(Barycenter, body, *args, **kwargs)
        elif body > -1000:
            body = object.__new__(Spacecraft, body, *args, **kwargs)
        elif body >= -100000:
            body = object.__new__(Instrument, body, *args, **kwargs)
        else:
            body = object.__new__(Spacecraft, body, *args, **kwargs)
        return body

    def __init__(self, body):
        self._id = body
        self._name = spice.bodc2n(body)
        self._frame = None
        if self._name is None:
            msg = 'Body() {} is not a valid ID.'
            raise ValueError(msg.format(body))

    def __str__(self):
        return self.__class__.__name__ + ' {} (ID {})'.format(self.name,
            self.id)

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

    def state(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
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

    def single_state(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkezr(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer))

    def position(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
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

    def single_position(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkpos(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer)[0])

    def speed(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
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

    def single_speed(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        return self.single_state(time, observer, frame, abcorr)[3:]

    def rotation(self, times, target='ECLIPJ2000'):
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
        if isinstance(target, Body):
            target = target._frame or target.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            result = []
            valid_times = []
            for time in times:
                with ignored(spice.SpiceError):
                    result.append(spice.pxform(self._frame or self.name,
                        target, Time.fromposix(time).et()))
                    valid_times.append(time)
            return numpy.array(valid_times), [numpy.array(item).reshape(3, 3)
                for item in result]
        msg = 'rotation() Real or Iterable argument expected, got {}.'
        raise TypeError(msg.format(type(times)))

    def single_rotation(self, time, target='ECLIPJ2000'):
        if isinstance(target, Body):
            target = target._frame or destination.name
        return numpy.array(spice.pxform(self._frame or self.name, target,
            Time.fromposix(time).et())).reshape(3, 3)

    def time_window_position(self):
        return Kernel.TIMEWINDOWS_POS[self.id]

    def time_window_rotation(self):
        return Kernel.TIMEWINDOWS_ROT[self.id]



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
        self._frame = 'IAU_' + self._name

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

class Star(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing the sun.

    Only used for the sun (ID 10) at the moment.
    '''
    def __init__(self, body_id):
        super(Star, self).__init__(body_id)
        self._frame = 'IAU_SUN'

    def parent(self):
        return Body(0)

    def children(self):
        return list(_iterbodies(199, 1000, 100))
