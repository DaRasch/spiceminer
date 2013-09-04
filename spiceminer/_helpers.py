#!/usr/bin/env python
#-*- coding:utf-8 -*-

import calendar
import datetime as dt

from contextlib import contextmanager

__all__ = ['frange', 'dtrange']


@contextmanager
def ignored(exception):
    try:
        yield
    except exception as e:
        pass


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
    argc = len(args)
    args = mutator(args)
    if argc < 1:
        msg = '{} expects at least 1 argument, got {}.'.format(fname, argc)
        raise TypeError(msg)
    elif argc == 1:
        start, stop, step = 0, next(args), 1
    elif argc == 2:
        start, stop, step = next(args), next(args), 1
    elif argc == 3:
        start, stop, step = next(args), next(args), next(args)
    else:
        msg = '{} expects at most 3 arguments, got {}.'.format(fname, argc)
        raise TypeError(msg)
    if (start < stop and step > 0):
        while start < stop:
            yield start
            start += step
    elif (start > stop and step < 0):
        while start > stop:
            yield start
            start -= step

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
                arg.utctimetuple())) + (arg.microseconds / 1000.0)
        yield args[2].total_seconds()
    return _basicrange(args, _datetimemutator, 'dtrange')
