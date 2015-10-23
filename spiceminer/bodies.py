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
    '''Iterate over all bodies with ids in the given range.'''
    for i in xrange(start, stop, step):
        with ignored(ValueError):
            yield Body(i)

def _typecheck(times, observer, frame):
    '''Check and convert arguments for spice interface methods.'''
    try:
        times = (float(t) for t in times)
    except TypeError:
        times = [float(times)]
    observer = Body(observer).name
    if frame not in ('J2000', 'ECLIPJ2000'):
        frame = Body(frame)
        frame = frame._frame or frame.name
    return times, observer, frame

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


class _BodyMeta(type):
    def __call__(cls, body):
        # Check and convert type
        if isinstance(body, cls):
            id_ = body.id
        elif isinstance(body, basestring):
            id_ = spice.bodn2c(body)
            if id_ is None:
                raise ValueError("Got invalid name '{}'".format(body))
        elif isinstance(body, int):
            id_ = body
        else:
            msg = "'int' or 'str' argument expected, got '{}'"
            raise TypeError(msg.format(type(body)))
        if id_ not in set.union(set(), *(k.ids for k in Kernel.LOADED)):
            # TODO: implement better id-collection
            msg = "No loaded 'Body' with ID or name '{}'"
            raise ValueError(msg.format(body))
        # Create correct subclass
        if id_ > 2000000:
            body = object.__new__(Asteroid)
        elif id_ > 1000000:
            body = object.__new__(Comet)
        elif id_ > 1000:
            body = object.__new__(Body)
        elif id_ > 10:
            if id_ % 100 == 99:
                body = object.__new__(Planet)
            else:
                body = object.__new__(Satellite)
        elif id_ == 10:
            body = object.__new__(Star)
        elif id_ >= 0:
            body = object.__new__(Barycenter)
        elif id_ > -1000:
            body = object.__new__(Spacecraft)
        elif id_ >= -100000:
            body = object.__new__(Instrument)
        else:
            body = object.__new__(Spacecraft)
        body.__init__(id_)
        return body

    @property
    def LOADED(cls):
        #TODO: Move implementation to kernel.highlevel.Kernel
        ids = set.union(set(), *(k.ids for k in Kernel.LOADED))
        for i in sorted(ids):
            body = Body(i)
            if isinstance(body, cls):
                yield body

    def all(cls):
        return cls.LOADED


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
    __metaclass__ = _BodyMeta

    _ABCORR = 'NONE'

    #TODO: implement Body.LOADED

    def __init__(self, body):
        self._id = body
        self._name = spice.bodc2n(body) or str(self._id)
        self._frame = None

    def __str__(self):
        return self.__class__.__name__ + ' {} (ID {})'.format(self.name,
            self.id)

    def __repr__(self):
        return self.__class__.__name__ + "('{}')".format(self.name)

    def __hash__(self):
        return self.id

    @property
    def id(self):
        '''The ID of this body.'''
        return self._id

    @property
    def name(self):
        '''The name of this body.'''
        return self._name

    @property
    def parent(self):
        '''Get the body that this body is bound to (orbiting or physical
        attachment).
        '''
        return None

    @property
    def children(self):
        '''Get the bodies bound to this body.'''
        return []

    def state(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position and speed of this body relative to the observer
        in a specific reference frame.

        Parameters
        ----------
        times: float|iterable
            The time(s) for which to get the state.
        observer: str|Body
            Position and speed are measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body|{'ECLIPJ2000', 'J2000'}
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        state: ndarray
            The nx7 array where the rows are time, position x, y, z and speed
            x, y, z.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.

        SpiceError
            If necessary information is missing.
        '''
        times, observer, frame = _typecheck(times, observer, frame)
        result = []
        for time in times:
            with ignored(spice.SpiceError):
                data = spice.spkezr(self.name, Time.fromposix(time).et(),
                    frame, abcorr or Body._ABCORR, observer)
                result.append([time] + data[0] + [data[1]])
        return numpy.array(result).transpose()

    def single_state(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        # TODO: use _typecheck, make sure to handle single time
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkezr(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer))

    def position(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position of this body relative to the observer in a
        specific reference frame.

        Parameters
        ----------
        times: float|iterable
            The time(s) for which to get the position.
        observer: str|Body
            Position is measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body|{'ECLIPJ2000', 'J2000'}
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        position: ndarray
            The nx4 array where the rows are time, position x, y, z.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.

        SpiceError
            If necessary information is missing.
        '''
        times, observer, frame = _typecheck(times, observer, frame)
        result = []
        for time in times:
            with ignored(spice.SpiceError):
                result.append([time] + spice.spkpos(self.name,
                Time.fromposix(time).et(), frame, abcorr or Body._ABCORR,
                observer)[0])
        return numpy.array(result).transpose()

    def single_position(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        # TODO: use _typecheck, make sure to handle single time
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(frame, Body):
            frame = frame._frame or frame.name
        return numpy.array(spice.spkpos(self.name, Time.fromposix(time).et(),
            frame, abcorr or Body._ABCORR, observer)[0])

    def speed(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the speed of this body relative to the observer in a specific
        reference frame.

        Parameters
        ----------
        times: float|iterable
            The time(s) for which to get the speed.
        observer: str|Body
            Position is measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body|{'ECLIPJ2000', 'J2000'}
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        speed: ndarray
            The nx4 array where the rows are time, speed x, y, z.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.

        SpiceError
            If necessary information is missing.
        '''
        times, observer, frame = _typecheck(times, observer, frame)
        data = self.state(times, observer, frame, abcorr)
        return data[numpy.array([True] + [False] * 3 + [True] * 3)]

    def single_speed(self, time, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        return self.single_state(time, observer, frame, abcorr)[3:]

    def rotation(self, times, target='ECLIPJ2000'):
        '''Get the rotation matrix for transforming the rotating of this body
        from its own reference frame to that of the target.

        Parameters
        ----------
        times: float|iterable
            The time(s) for which to get the matrix.
        target: Body|{'ECLIPJ2000', 'J2000'}
            Reference frame to transform to.

        Returns
        -------
        times: ndarray
            The times for which rotation matrices where generated.
        matrices: list
            List of 3x3 rotation matrices.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.

        SpiceError
            If necessary information is missing.
        '''
        times, target, _ = _typecheck(times, target, 'ECLIPJ2000')
        result = []
        valid_times = []
        for time in times:
            with ignored(spice.SpiceError):
                result.append(spice.pxform(self._frame or self.name,
                    target, Time.fromposix(time).et()))
                valid_times.append(time)
        return numpy.array(valid_times), [numpy.array(item).reshape(3, 3)
            for item in result]

    def single_rotation(self, time, target='ECLIPJ2000'):
        if isinstance(target, Body):
            target = target._frame or destination.name
        return numpy.array(spice.pxform(self._frame or self.name, target,
            Time.fromposix(time).et())).reshape(3, 3)

    def proximity(self, time, distance, classes=None):
        '''Get other bodies at most `distance` km away from this body.

        Parameters
        ----------
        time: float
            The time to look at.
        distance: float
            The maximum distance at which bodies are included in the results.
        classes: type
            Filter to select certain types of bodies to look for.

        Returns
        -------
        bodies: iterator
            The selected bodies.

        Raises
        ------
        SpiceError
            If necessary information is missing.
        '''
        for body in Body.LOADED:
            try:
                pos = body.single_position(time, observer=self)[1:]
            except spice.SpiceError:
                continue
            dist = numpy.sqrt((pos ** 2).sum())
            if isinstance(body, tuple(classes or [Body])):
                if body.id != self.id and dist <= distance:
                    yield body


    def time_window_position(self):
        return Kernel.TIMEWINDOWS_POS[self.id]

    def time_window_rotation(self):
        return Kernel.TIMEWINDOWS_ROT[self.id]



class Asteroid(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing asteroids.

    Asteroids are ephimeris objects with IDs > 200000.
    '''
    def __init__(self, body):
        super(Asteroid, self).__init__(body)


class Barycenter(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing a
    barycenter of an ephimeris object and all of its satellites.

    Barycenters are ephimeris objects with IDs between 0 and 9.
    '''
    def __init__(self, body):
        super(Barycenter, self).__init__(body)


class Comet(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing comets.

    Comets are ephimeris objects with IDs between 100000 and 200000.
    '''
    def __init__(self, body):
        super(Comet, self).__init__(body)


class Instrument(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing instruments
    mounted on spacecraft (including rovers and their instruments).

    Instruments are ephimeris objects with IDs between -1001 and -10000.
    '''
    def __init__(self, body):
        super(Instrument, self).__init__(body)

    @property
    def parent(self):
        offset = 0 if self.id % 1000 == 0 else -1
        spacecraft_id = self.id / 1000 + offset
        return Body(spacecraft_id)


class Planet(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing planets.

    Planets are ephimeris objects with IDs between 199 and 999 with
    pattern [1-9]99.
    '''
    def __init__(self, body):
        super(Planet, self).__init__(body)
        self._frame = 'IAU_' + self._name

    @property
    def parent(self):
        return Body(10)

    @property
    def children(self):
        return list(_iterbodies(self.id - 98, self.id))


class Satellite(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing satellites
    (natural bodies orbiting a planet).

    Satellites are ephimeris objects with IDs between 101 and 998 with
    pattern [1-9][0-9][1-8].
    '''
    def __init__(self, body):
        super(Satellite, self).__init__(body)
        self._frame = 'IAU_' + self._name

    @property
    def parent(self):
        return Body(self.id - self.id % 100 + 99)


class Spacecraft(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing spacecraft.

    Spacecraft are ephimeris objects with IDs between -1 and -999 or < -99999.
    '''
    def __init__(self, body):
        super(Spacecraft, self).__init__(body)

    @property
    def children(self):
        return list(_iterbodies(self.id * 1000, self.id * 1000 - 1000, -1))

class Star(Body):
    '''Subclass of :py:class:`~spiceminer.bodies.Body` representing the sun.

    Only used for the sun (ID 10) at the moment.
    '''
    def __init__(self, body):
        super(Star, self).__init__(body)
        self._frame = 'IAU_SUN'

    @property
    def parent(self):
        return Body(0)

    @property
    def children(self):
        return list(_iterbodies(199, 1000, 100))
