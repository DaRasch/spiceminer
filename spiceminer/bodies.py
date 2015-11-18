#-*- coding:utf-8 -*-

import numbers
import collections

import numpy

from . import _spicewrapper as spice
from .time_ import Time
from ._helpers import ignored
from .kernel.highlevel import Kernel

__all__ = ['Body', 'Asteroid', 'Barycenter', 'Comet', 'Instrument',
            'Planet', 'Satellite', 'Spacecraft', 'Star']


### Helpers ###
def _iterbodies(start, stop, step=1):
    '''Iterate over all bodies with ids in the given range.'''
    for i in xrange(start, stop, step):
        with ignored(ValueError):
            yield Body(i)

def _typecheck(times, observer=None, frame='ECLIPJ2000'):
    '''Check and convert arguments for spice interface methods.'''
    try:
        times = (float(t) for t in times)
    except TypeError:
        times = [float(times)]
    if observer is not None:
        observer = Body(observer).name
    if frame not in ('J2000', 'ECLIPJ2000'):
        frame = Body(frame)
        frame = frame._frame or frame.name
    return times, observer, frame


class _BodyMeta(type):
    '''Metaclass for Body to seperate instance creation from initialisation and
    to force methods on the class level only.'''
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
        if id_ not in set.union({0}, *(k.ids for k in Kernel.LOADED)):
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


### Public API ###

class Body(object):
    '''Base class for representing ephimeres objects.

    Parameters
    ----------
    body: str or int or Body
        The name or ID of the requested body.

    Raises
    ------
    ValueError
        If the provided name/ID doesn't reference a loaded body.
    TypeError
        If `body` has the wrong type.

    Attributes
    ----------
    *classattribute* LOADED: set of body
        All available bodies.
    id: int
        The reference id of the body for the backend. Guaranteed to be unique.
    name: str
        The name of the body.
    times_pos: list of tuple of Time
        Start-end-tuples of all time frames where the position of the body is
        available.
    times_rot: list of tuple of Time
        Start-end-tuples of all time frames where the rotation of the body is
        available.
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
    def times_pos(self):
        '''The time intervals for which positions are defined.'''
        return Kernel.TIMEWINDOWS_POS[self.id]

    @property
    def times_rot(self):
        '''The time intervals for which rotations are defined.'''
        return Kernel.TIMEWINDOWS_ROT[self.id]

    @property
    def parent(self):
        '''The body that this body is bound to (orbiting or physical
        attachment).
        '''
        return None

    @property
    def children(self):
        '''The bodies bound to this body (orbiting around it permanently and
        thereby included in its barycenter).'''
        return []

    def state(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position and speed of this body relative to the observer
        in a specific reference frame.

        Parameters
        ----------
        times: floator iterable of float
            The time(s) for which to get the state.
        observer: str or Body, optional
            Position and speed are measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        state: array_like
            The nx7 array where the rows are time, position x, y, z and speed
            x, y, z.
            Positions are in km and speeds in km/sec.

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

    def position(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position of this body relative to the observer in a
        specific reference frame.

        Parameters
        ----------
        times: float or iterable of float
            The time(s) for which to get the position.
        observer: str or Body, optional
            Position is measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        position: array_like
            The nx4 array where the rows are time, position x, y, z.
            Positions are in km.

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

    def speed(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the speed of this body relative to the observer in a specific
        reference frame.

        Parameters
        ----------
        times: float or iterable of float
            The time(s) for which to get the speed.
        observer: str or Body, optional
            Position is measured relative to this body.
            The rotation of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        speed: array_like
            The nx4 array where the rows are time, speed x, y, z.
            Speeds in km/sec.

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

    def rotation(self, times, target='ECLIPJ2000'):
        '''Get the rotation matrix for transforming the rotating of this body
        from its own reference frame to that of the target.

        Parameters
        ----------
        times: float or iterable of float
            The time(s) for which to get the matrix.
        target: Body or {'ECLIPJ2000', 'J2000'}, optional
            Reference frame to transform to.

        Returns
        -------
        times: array_like
            The times for which rotation matrices where generated.
        matrices: list of array_like
            List of 3x3 rotation matrices.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.
        SpiceError
            If necessary information is missing.
        '''
        times, _, target = _typecheck(times, None, target)
        result = []
        valid_times = []
        for time in times:
            with ignored(spice.SpiceError):
                result.append(spice.pxform(self._frame or self.name,
                    target, Time.fromposix(time).et()))
                valid_times.append(time)
        return numpy.array(valid_times), [numpy.array(item).reshape(3, 3)
            for item in result]

    def proximity(self, time, distance, classes=None):
        '''Get other bodies at most `distance` km away from this body.

        Parameters
        ----------
        time: float
            The time to look at.
        distance: float
            The maximum distance in km at which bodies are included in the results.
        classes: type
            Filter to select certain types of bodies to look for.

        Yields
        ------
        Body
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
            if isinstance(body, tuple(classes) or (Body,)):
                if body.id != self.id and dist <= distance:
                    yield body


class Asteroid(Body):
    '''Bodies representing asteroids.

    Asteroids are ephimeris objects with IDs > 200000.
    '''
    def __init__(self, body):
        super(Asteroid, self).__init__(body)


class Barycenter(Body):
    '''Bodies representing a barycenter of an ephimeris object and all of its
    satellites.

    Barycenters are ephimeris objects with IDs between 0 and 9.
    '''
    def __init__(self, body):
        super(Barycenter, self).__init__(body)


class Comet(Body):
    '''Bodies representing comets.

    Comets are ephimeris objects with IDs between 100000 and 200000.
    '''
    def __init__(self, body):
        super(Comet, self).__init__(body)


class Instrument(Body):
    '''Bodies representing instruments mounted on spacecraft (including rovers
    and their instruments).

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
    '''SBodies representing planets.

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
    '''Bodies representing satellites (natural bodies orbiting a planet e.g.
    moons).

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
    '''Bodies representing spacecraftand rovers.

    Spacecraft are ephimeris objects with IDs between -1 and -999 or < -99999.
    '''
    def __init__(self, body):
        super(Spacecraft, self).__init__(body)

    @property
    def children(self):
        return list(_iterbodies(self.id * 1000, self.id * 1000 - 1000, -1))

class Star(Body):
    '''Body representing the sun.

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
