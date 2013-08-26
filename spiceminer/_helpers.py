#!/usr/bin/env python
#-*- coding:utf-8 -*-

from contextlib import contextmanager

__all__ = ['ignored', 'frange', 'dtrange']


@contextmanager
def ignored(exception):
    try:
        yield
    except exception as e:
        pass


### Some range-functions for easier usage of bodies.Body.get_data ###
def _basicrange(args, mutator, fname):
    argc = len(args)
    args = mutator(args)
    if argc < 1:
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
    if (start < stop and step > 0):
        while start < stop:
            yield start
            start += step
    elif (start > stop and step < 0):
        while start > stop:
            yield start
            start -= step

def frange(*args):
    def _floatmutator(args):
        return (float(arg) for arg in args)
    return _basicrange(args, _floatmutator, 'frange')

def dtrange(*args):
    def _datetimemutator(args):
        for arg in args[:2]:
            yield float(Time.fromdatetime(arg))
        yield args[2].total_seconds()
    return _basicrange(args, _datetimemutator, 'dtrange')
