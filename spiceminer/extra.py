#-*- coding:utf-8 -*-

import calendar

import numpy as np

from numpy.linalg import norm

__all__ = ['angle', 'sphere2cartesian', 'cartesian2sphere']

UX, UY, UZ = np.identity(3)


def angle(v0, v1):
    '''Calculate the angle between 2 vectors.

    Parameters
    ----------
    v0, v1: array-like
        The vectors to measure the angle between. Must have shape (n>1,) or
        (n>1, m) where n is the dimension of the vector and m the number of
        vectors.

    Returns
    -------
    array-like
        The angles between `v0` and `v1` in radians.

    Raises
    ------
    ValueError
        If one or both vector-arrays do not fit the requirements.
    '''
    def iangle(v0, v1):
        v0 = v0 / norm(v0, axis=0)
        v1 = v1 / norm(v1, axis=0)
        for x, y in zip(v0.T, v1.T):
            radians = np.arccos(np.dot(x, y))
            if np.isnan(radians):
                if (x == y).all():
                    radians = 0.0
                else:
                    radians = np.pi
            yield radians

    if v0.shape != v1.shape:
        msg = 'shapes {} and {} not equal'
        raise ValueError(msg.format(v0.shape, v1.shape))
    if v0.shape[0] < 2:
        msg = 'vectors must havew at least 2 dimensions, got {}'
        raise ValueError(msg.format(v0.shape[0]))
    if len(v0.shape) > 2:
        msg = 'v0 and v1 may only be 1-D or 2-D, got {}-D'
        raise ValueError(msg.format(len(v0.shape)))
    if len(v0.shape) == 1:
        v0 = np.array([[item] for item in v0])
        v1 = np.array([[item] for item in v1])
    return np.fromiter(iangle(v0, v1), dtype=float, count=v0.shape[1])

def clockwise_angle(v0, v1):
    '''Calculates the clockwise angle between vectors. Always uses the
    clockwise angle, allowing angles 0 <= x < 2 * pi.

    Parameters
    ----------
    v0, v1: array-like
        The vectors to measure the angle between. Must have shape (n>1,) or
        (n>1, m) where n is the dimension of the vector and m the number of
        vectors.

    Returns
    -------
    array-like
        The angles between `v0` and `v1` in radians.

    Raises
    ------
    ValueError
        If one or both vector-arrays do not fit the requirements.
    '''
    def iclockwise_angle(v0, v1):
        radians = angle(v0, v1)
        for x, y, rad in zip(v0, v1, radians):
            normal = np.cross(x, y)
            normal = normal / norm(normal)
            direction = np.dot(UZ, normal)
            if direction > 0:
                # Angle greater pi
                yield 2 * pi - radians
            elif direction < 0:
                # Angle smaller pi
                yield radians
            else:
                # If the angle between up and normal is pi/2
                # (up 'dot' normal == 0), it is impossible to decide which way
                # is clockwise
                # I am ignoring that.
                yield radians
    return np.fromiter(iclockwise_angle(v0, v1), dtype=float, count=v0.shape[1])


### Coordinate transformations ###
def cartesian2sphere(vectors):
    '''Convert cartesian to spherical coordinates.

    Parameters
    ----------
    vectors: array-like
        The vectors to transform. Must have shape (3,) or (3, n) where n is
        the number of vectors.
        Vectors should have the form [x, y, z].

    Returns
    -------
    array-like
        The converted coordinates as [r, phi, theta].

    Raises
    ------
    ValueError
        If the vector-array does not fit the requirements.
    '''
    if vectors.shape[0] != 3:
        msg = 'shape must be (3,) or (3,n), got {}'
        raise ValueError(msg.format(vectors.shape))
    x, y, z = vectors
    r = np.sqrt(np.sum(vectors ** 2, 0))
    phi = np.arctan2(y, x)
    theta = np.arccos(z / r)
    return np.array([r, phi, theta])

def sphere2cartesian(vectors):
    '''Convert spherical to cartesian coordinates.

    Parameters
    ----------
    vectors: array-like
        The vectors to transform. Must have shape (3,) or (3, n) where n is
        the number of vectors.
        Vectors should have the form [r, phi, theta].

    Returns
    -------
    array-like
        The converted coordinates as [x, y, z].

    Raises
    ------
    ValueError
        If the vector-array does not fit the requirements.
    '''
    if vectors.shape[0] != 3:
        msg = 'shape must be (3,) or (3,n), got {}'
        raise ValueError(msg.format(vectors.shape))
    r, phi, theta = vectors
    sinphi = np.sin(phi)
    x = r * np.cos(theta) * sinphi
    y = r * np.sin(theta) * sinphi
    z = r * np.cos(phi)
    return np.array([x, y, z])


### Some range-functions for easier usage of bodies.Body.state() etc. ###
def _range_base(start, stop, step):
    '''Simple range function to be used in more complex wrappers.
    '''
    if step > 0:
        while start < stop:
            yield start
            start += step
    elif step < 0:
        while start > stop:
            yield start
            start += step

def _meta_range(args, mutator, fname):
    '''A metafunction to build xrange-like functions.

    :type args: ???
    :arg args: The arguments to transform to ``float``.

    :type mutator: ``generator``
    :arg mutator: A function that transforms the arguments to floats and yields
        the results individually.

    :type fname: ``str``
    :arg fname: Name of function to show in error messages.

    :return: (``generator``) -- All values in ``[start, stop)`` seperated by
        ``step``.
    :raises: (``TypeError``) -- If the number of arguments is 0 or more than 3.
    '''
    argc = len(args)
    args = mutator(args)
    if argc == 0:
        msg = '{} expects at least 1 argument, got {}'.format(fname, argc)
        raise TypeError(msg)
    elif argc == 1:
        start, stop, step = 0, next(args), 1
    elif argc == 2:
        start, stop, step = next(args), next(args), 1
    elif argc == 3:
        start, stop, step = next(args), next(args), next(args)
    else:
        msg = '{} expects at most 3 arguments, got {}'.format(fname, argc)
        raise TypeError(msg)
    return _range_base(start, stop, step)


def frange(*args):
    '''Functionally equivalent to builtin ``xrange()``, but can also handle
    ``float`` and anything that can be converted to ``float``.

    :type start: has ``__float__()``
    :arg start: Value to start from (0 if omitted).

    :type stop: has ``__float__()``
    :arg stop: Value to end before.

    :type step: has ``__float__()``
    :arg step: Size of increments (1 if omitted).

    :return: (``float-generator``) -- All values in ``[start, stop)`` seperated
        by ``step``.
    :raises: (``TypeError``) -- If the number of arguments is 0 or more than 3.
    '''
    def _floatmutator(args):
        return (float(arg) for arg in args)
    return _meta_range(args, _floatmutator, 'frange')

def dtrange(*args):
    '''Functionally equivalent to builtin ``xrange()``, but uses ``datetime``
    instead.

    :type start: ``datetime``
    :arg start: Value to start from (equivalent to 0 if omitted).

    :type stop: ``datetime``
    :arg stop: Value to end before .

    :type step: ``timedelta``
    :arg step: Size of increments (1 second if omitted).

    :return: (``float-generator``) -- All values in ``[start, stop)`` seperated
        by ``step``.
    :raises: (``TypeError``) -- If the number of arguments is 0 or more than 3.
    '''
    def _datetimemutator(args):
        for arg in args[:2]:
            try:
                yield float(calendar.timegm(
                    arg.utctimetuple())) + (arg.microsecond / 1000000.0)
            except AttributeError:
                raise TypeError('expected datetime, got {}'.format(type(arg)))
        try:
            yield args[2].total_seconds()
        except AttributeError:
            raise TypeError('expected timedelta, got {}'.format(type(arg)))
    return _meta_range(args, _datetimemutator, 'dtrange')
