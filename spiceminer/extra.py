#-*- coding:utf-8 -*-

import calendar
import datetime as dt

from numpy import arccos, dot, isnan, pi
from numpy.linalg import norm

__all__ = ['angle', 'frange', 'dtrange']


def angle(v0, v1):
    u_v0 = v0 / norm(v0)
    u_v1 = v1 / norm(v1)
    angle = arccos(dot(u_v0, u_v1))
    if isnan(angle):
        if (u_v0 == u_v1).all():
            return 0.0
        else:
            return pi
    return angle


### Some range-functions for easier usage of bodies.Body.state() etc. ###
def _basicrange(args, mutator, fname):
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

    .. WARNING:: As indicated by the leading underscore, this function is not
        meant to be used if you don't know what you are doing. You have been
        warned!
    '''
    def _range(start, stop, step):
        if step > 0:
            while start < stop:
                yield start
                start += step
        elif step < 0:
            while start > stop:
                yield start
                start += step
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
    return _range(start, stop, step)

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
    return _basicrange(args, _floatmutator, 'frange')

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
    return _basicrange(args, _datetimemutator, 'dtrange')
