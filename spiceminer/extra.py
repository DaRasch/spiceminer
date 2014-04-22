#-*- coding:utf-8 -*-

import calendar

import numpy as np

from numpy import arccos, dot, cross, isnan, pi
from numpy.linalg import norm

__all__ = ['angle', 'clockwise_angle', 'frange', 'dtrange']

UX, UY, UZ = np.identity(3)


def angle(v0, v1, center=None):
    '''Calculates the absolute angle between 2 vectors (one-dimensional
    arrays).

    :type v0: ``numpy.ndarray``
    :arg v0: A vector.
    :type v1: ``numpy.ndarray``
    :arg v1: A vector.
    :type center: ``numpy.ndarray``
    :arg center: The point to use as zero-vector.
    :return: (``float``) -- The angle between *v0* and *v1* in radians (0-pi).
    :raises: Nothing.
    '''
    if center is None:
        u_v0 = v0 / norm(v0)
        u_v1 = v1 / norm(v1)
    else:
        u_v0 = (v0 - center) / norm(v0)
        u_v1 = (v1 - center) / norm(v1)
    radians = arccos(dot(u_v0, u_v1))
    if isnan(radians):
        if (u_v0 == u_v1).all():
            return 0.0
        else:
            return pi
    return radians

def clockwise_angle(v0, v1, center=None, up=None):
    '''Calculates the clockwise angle between 2 vectors (one-dimensional
    arrays). Always uses the clockwise angle, allowing angles greater than
    pi.

    :type v0: ``numpy.ndarray``
    :arg v0: A vector.
    :type v1: ``numpy.ndarray``
    :arg v1: A vector.
    :type center: ``numpy.ndarray``
    :arg center: The point around which the angle is calculated.
      **Default:** [0,0,0]
    :type up: ``numpy.array``
    :arg up: The vector defining which side of the plane defined by *v0* and
      *v1* is up.
      **Default:** [0,0,1]
    :return: (``float``) -- The clockwise angle between *v0* and *v1* around
      *center* in radians.
    :raises:
      (``ValueError``) -- If *up* lies in the plane formed by *v0* and *v1*.
    '''
    radians = angle(v0, v1, center)
    if up is None:
        up = UZ
    else:
        up = up / norm(up)
    normal = cross(v0, v1)
    normal = normal / norm(normal)
    direction = dot(up, normal)
    if direction > 0:
        # Angle greater pi
        return 2 * pi - radians
    elif direction < 0:
        # Angle smaller pi
        return radians
    else:
        # If the angle between up and normal is pi/2 (up 'dot' normal == 0), it
        # is impossible to decide which way is clockwise
        raise ValueError('Bad up-vector: ' + str(up))


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
            yield float(calendar.timegm(
                arg.utctimetuple())) + (arg.microsecond / 1000000.0)
        yield args[2].total_seconds()
    return _meta_range(args, _datetimemutator, 'dtrange')
