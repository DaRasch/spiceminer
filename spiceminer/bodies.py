#-*- coding:utf-8 -*-

import collections

import numpy

from . import util
from . import _spicewrapper as spice
from .time_ import Time

__all__ = ['Body', 'Asteroid', 'Barycenter', 'Comet', 'Instrument',
    'Planet', 'Satellite', 'Spacecraft', 'Star']


### Special frame handlers ###
class FrameDecorator(object):
    '''Decorator for frames which are not spice objects.'''

    FRAMES = {}

    def __init__(self, base, name=None):
        self.base = base
        self.name = name

    def __call__(self, frame_cls):
        transform = frame_cls()
        with util.ignored(KeyError):
            while True:
                base_base, base_transform = self.__class__.FRAMES[self.base]
                transform = _MergedFrame(base_transform, transform)
                self.base = base_base
        if self.name is None:
            self.name = frame_cls.__name__.strip('_').replace('_', ' ')
        self.__class__.FRAMES[self.name.upper()] = (self.base, transform)
        return frame_cls

    @classmethod
    def convert(cls, frame):
        '''Convert strings representing special frames to their base frame and
        a SpecialFrame instance with the relevant transformative methods.'''
        frame = frame.upper()
        if frame in ('J2000', 'ECLIPJ2000'):
            transform = SpecialFrame()
        else:
            frame, transform = cls.FRAMES[frame]
        return frame, transform


class SpecialFrame(object):
    '''Template for custom frames.'''
    def state(self, output):
        return output
    #def speed(self, output):
    #    return output
    def position(self, output):
        return output
    def rotation(self, output):
        return output

class _MergedFrame():
    '''Frame that applies the transforms of multiple special frames.'''

    def __init__(self, *frames):
        self.frames = []
        for frame in frames:
            if isinstance(frame, self.__class__):
                self.frames += frame.frames
            else:
                self.frames.append(frame)

    def state(self, output):
        for frame in self.frames:
            output = frame.state(output)

    def position(self, output):
        for frame in self.frames:
            output = frame.position(output)

    def rotation(self, output):
        for frame in self.frames:
            output = frame.rotation(output)


@FrameDecorator('SUN')
class _Carrington(SpecialFrame):
    '''This frame is just an alias for 'SUN'.'''
    pass


### Helpers ###
def _iterbodies(start, stop, step=1):
    '''Iterate over all bodies with ids in the given range.'''
    for i in range(start, stop, step):
        with util.ignored(ValueError):
            yield Body(i)

def _prepare_times(times):
    if isinstance(times, basestring):
        times = [float(times)]
    try:
        times = (float(t) for t in times)
    except TypeError:
        times = [float(times)]
    return times

def _prepare_observer(body):
    return Body(body).name

def _prepare_frame(frame):
    try:
        frame, transform = FrameDecorator.convert(frame)
    except (KeyError, AttributeError):
        frame = Body(frame)
        frame = frame._frame or frame.name
        transform = SpecialFrame()
    return frame, transform

def _typecheck(times, observer=None, frame='ECLIPJ2000'):
    '''Check and convert arguments for spice interface methods.'''
    times = _prepare_times(times)
    if observer:
        observer = _prepare_observer(observer)
    frame, transform = _prepare_frame(frame)
    return times, observer, frame, transform


class _BodyMeta(type):
    '''Metaclass for Body to seperate instance creation from initialisation and
    to force methods on the class level only.'''

    _ID_COUNTER = collections.Counter()
    _ID_MAP = {}

    def __init__(cls, name, bases, namespace):
        super(cls.__class__, cls).__init__(name, bases, namespace)
        cls.LOADED = set()
        cls._REGISTRY = set(base for base in bases if isinstance(cls, cls.__class__))
        cls._REGISTRY.add(cls)

    def _register(cls, body):
        for kls in cls._REGISTRY:
            kls.LOADED.add(body)

    def _unregister(cls, body):
        for kls in cls._REGISTRY:
            kls.LOADED.remove(body)

    def _make(cls, id_):
        if _BodyMeta._ID_COUNTER[id_] == 0:
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
            body.__class__._register(body)
            _BodyMeta._ID_MAP[id_] = body
        _BodyMeta._ID_COUNTER[id_] += 1

    def _delete(cls, id_):
        _BodyMeta._ID_COUNTER[id_] -= 1
        body = cls(id_)
        count = _BodyMeta._ID_COUNTER[id_]
        if count == 0:
            body.__class__._unregister(body)
            del _BodyMeta._ID_MAP[id_]
        elif count < 0:
            _BodyMeta._ID_COUNTER[id_] = 0
            msg = '{} with id {} is not loaded'
            raise ValueError(msg.format(cls.__name__, id_))

    def __call__(cls, body):
        # Check and convert type
        try:
            id_ = body.id
        except AttributeError:
            id_ = body
        try:
            id_ = int(float(id_))
        except TypeError:
            msg = "'Body', 'int' or 'str' argument expected, got '{}'"
            raise TypeError(msg.format(type(body)))
        except ValueError:
            id_ = spice.bodn2c(body)
            if id_ is None:
                raise ValueError("Got invalid name '{}'".format(body))
        if id_ not in _BodyMeta._ID_MAP:
            msg = "No loaded 'Body' with ID or name '{}'"
            raise ValueError(msg.format(body))
        return _BodyMeta._ID_MAP[id_]


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
        The reference id of the body. Guaranteed to be unique.
    name: str
        The name of the body.
    times_pos: list of tuple of Time
        Start-end-tuples of all times when the position of the body is
        available.
    times_rot: list of tuple of Time
        Start-end-tuples of all times when where the rotation of the body is
        available.
    parent: Body or None
        The Body that the Body is bound to either by gravitation (e.g moons) or
        by physical attachment (e.g Instruments of a spacecraft).
    children: list of Body
        The reverse of `parent`.
    '''
    __metaclass__ = _BodyMeta

    _ABCORR = 'NONE'

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
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def times_pos(self):
        return util.TIMEWINDOWS_POS[self]

    @property
    def times_rot(self):
        return util.TIMEWINDOWS_ROT[self]

    @property
    def parent(self):
        return None

    @property
    def children(self):
        return []

    def state(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position and speed of this body relative to the observer
        in a specific reference frame.

        Parameters
        ----------
        times: float or iterable of float
            UNIX timestamp(s) for which to get the state.
        observer: str or Body, optional
            The positional reference frame.
            Position and speed are measured relative to this body. The rotation
            of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
            ECLIPJ2000 and J2000 are not co-rotating. All others are
            co-rotating with their respective Body.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        state: ndarray of float
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
        times, observer, frame, transform = _typecheck(times, observer, frame)
        result = []
        for time in times:
            with util.ignored(spice.SpiceError):
                data = spice.spkezr(self.name, Time.fromposix(time).et(),
                    frame, abcorr or Body._ABCORR, observer)
                result.append([time] + data[0] + [data[1]])
        return transform.state(numpy.array(result).transpose())

    def position(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the position of this body relative to the observer in a
        specific reference frame.

        Parameters
        ----------
        times: float or iterable of float
            UNIX timestamp(s) for which to get the position.
        observer: str or Body, optional
            The positional reference frame.
            Position is measured relative to this body. The rotation
            of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
            ECLIPJ2000 and J2000 are not co-rotating. All others are
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        position: ndarray of float
            The nx4 array where the rows are time, position x, y, z.
            Positions are in km.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.
        SpiceError
            If necessary information is missing.
        '''
        times, observer, frame, transform = _typecheck(times, observer, frame)
        result = []
        for time in times:
            with util.ignored(spice.SpiceError):
                result.append([time] + spice.spkpos(self.name,
                Time.fromposix(time).et(), frame, abcorr or Body._ABCORR,
                observer)[0])
        return transform.position(numpy.array(result).transpose())

    def speed(self, times, observer='SUN', frame='ECLIPJ2000',
        abcorr=None):
        '''Get the speed of this body relative to the observer in a specific
        reference frame.

        Parameters
        ----------
        times: float or iterable of float
            UNIX timestamp(s) for which to get the position.
        observer: str or Body, optional
            The positional reference frame.
            Speed is measured relative to this body. The rotation
            of the bodies is ignored, see the `frame` keyword.
        frame: Body or {'ECLIPJ2000', 'J2000'}, optional
            The rotational reference frame.
            `ECLIPJ2000`: The earths ecliptic plane is used as the x-y-plane.
            `J2000`: The earths equatorial plane is used as the x-y-plane.
            ECLIPJ2000 and J2000 are not co-rotating. All others are
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        -------
        speed: ndarray of float
            The nx4 array where the rows are time, speed x, y, z.
            Speeds are in km/sec.

        Raises
        ------
        TypeError
            If an argument doesn't conform to the type requirements.
        SpiceError
            If necessary information is missing.
        '''
        #times, observer, _, _ = _typecheck(times, observer, frame)
        data = self.state(times, observer, frame, abcorr)
        return data[numpy.array([True] + [False] * 3 + [True] * 3)]

    def rotation(self, times, target='ECLIPJ2000'):
        '''Get the rotation matrix for transforming the rotating of this body
        from its own reference frame to that of the target.

        Parameters
        ----------
        times: float or iterable of float
            UNIX timestamp(s) for which to get the matrix.
        target: Body or {'ECLIPJ2000', 'J2000'}, optional
            Reference frame to transform to.

        Returns
        -------
        times: ndarray of float
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
        times = _prepare_times(times)
        target, transform = _prepare_frame(target)
        result = []
        valid_times = []
        for time in times:
            with util.ignored(spice.SpiceError):
                result.append(spice.pxform(self._frame or self.name,
                    target, Time.fromposix(time).et()))
                valid_times.append(time)
        result = numpy.array(valid_times), [numpy.array(item).reshape(3, 3)
            for item in result]
        return transform.rotation(result)

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
        for body in set().union(kls.LOADED for kls in (classes or [Body])):
            try:
                pos = body.position(time, observer=self, frame=self)[1:]
            except spice.SpiceError:
                continue
            if len(pos) == 0:
                continue
            dist = numpy.sqrt((pos ** 2).sum())
            if body != self and dist <= distance:
                yield body


class Asteroid(Body):
    '''Asteroids are ephimeris objects with IDs > 200000.'''
    def __init__(self, body):
        super(Asteroid, self).__init__(body)
        self._frame = 'IAU_' + self._name


class Barycenter(Body):
    '''Barycenters are ephimeris objects with IDs between 0 and 9.

    A barycenter is the center of mass of a planet and all of its moons.
    '''
    def __init__(self, body):
        super(Barycenter, self).__init__(body)

Body._make(0)


class Comet(Body):
    '''Comets are ephimeris objects with IDs between 100000 and 200000.'''
    def __init__(self, body):
        super(Comet, self).__init__(body)


class Instrument(Body):
    '''Instruments are ephimeris objects with IDs between -1001 and -10000.'''
    def __init__(self, body):
        super(Instrument, self).__init__(body)

    @property
    def parent(self):
        offset = 0 if self.id % 1000 == 0 else -1
        spacecraft_id = self.id / 1000 + offset
        return Body(spacecraft_id)

    def fov(self):
        '''Get the field of view of an instrument.

        Returns
        ------
        shape: {'POLYGON', 'RECTANGLE', 'CIRCLE', 'ELLIPSE'}
            The shape of the field of view.
        frame: Body
            The reference frame in which the field of view boundary vectors
            are defined.
        boresight: array_like
            Vector pointing in the direction of the center of the field of view.
        bounds: array_like
            Array of vectors (nx3) that point to the *corners* of the instrument
            field of view.

        Raises
        ------
        SpiceError
            If the instrument has no available field of view.

        For more information on the relation between shape and bounds, see
        `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/getfov_c.html#Detailed_Output>`_
        '''
        nt = collections.namedtuple('FOVParameters',
            ['shape', 'frame', 'boresight', 'bounds'])
        shape, frame, boresight, bounds = spice.getfov(self.id)
        frame = Body(frame)
        boresight = numpy.array(boresight)
        bounds = numpy.array(bounds).T
        return nt(shape, frame, boresight, bounds)

    def can_see(self, times, body, abcorr=None):
        '''Test if the Instrument can see a specified Body.

        Parameters
        ----------
        times: float or iterable of float
            The time(s) for which to get the visibility.
        body: str or Body
            The Body to test visibility for.
        abcorr: {'LT', 'LT+S', 'CN', 'CN+S', 'XLT', 'XLT+S', 'XCN', 'XCN+S'}, optional
            Aberration correction to be applied. For explanation see
            `here <http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkez_c.html#Detailed_Input>`_.

        Returns
        ------
        times: array-like of float
            UNIX timestamp(s) of all times for which the visibility could
            be tested.
        visibility: ndarray of bool
            If the Body was visible at the given time.
        '''
        times = _prepare_times(times)
        body = Body(body)
        frame, _ = _prepare_frame(body)
        observer = self.fov().frame
        result = []
        for t in times:
            with util.ignored(spice.SpiceError):
                visible = spice.fovtrg(self.name, body.name, 'POINT', frame,
                    abcorr or Body._ABCORR, observer.name,
                    Time.fromposix(t).et())
                result.extend([float(t), not visible])
        return numpy.ma.array(result[::2], mask=result[1::2])


class Planet(Body):
    '''Planets are ephimeris objects with IDs between 199 and 999 with
    pattern [1-9]99.'''
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
    '''Satellites are ephimeris objects with IDs between 101 and 998 with
    pattern [1-9][0-9][1-8].

    Satellites are natural bodies orbiting a planet e.g. moons.
    '''
    def __init__(self, body):
        super(Satellite, self).__init__(body)
        self._frame = 'IAU_' + self._name

    @property
    def parent(self):
        return Body(self.id - self.id % 100 + 99)


class Spacecraft(Body):
    '''Spacecraft are ephimeris objects with IDs between -1
    and -999 or < -99999.'''
    def __init__(self, body):
        super(Spacecraft, self).__init__(body)

    @property
    def children(self):
        return list(_iterbodies(self.id * 1000, self.id * 1000 - 1000, -1))


class Star(Body):
    '''Only used for the sun (ID 10) at the moment.'''
    def __init__(self, body):
        super(Star, self).__init__(body)
        self._frame = 'IAU_SUN'

    @property
    def parent(self):
        return Body(0)

    @property
    def children(self):
        return list(_iterbodies(199, 1000, 100))
