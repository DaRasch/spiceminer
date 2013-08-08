#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections
import numbers
import numpy

import spice

from spiceminer._time import Time
from spiceminer._helpers import ignored

__all__ = ['makebody']


_CACHE = {}

### factory function ###
def makebody(body_id):
    if body_id in _CACHE:
        body = _CACHE[body_id]
    elif body_id > 2000000:
        body = Asteroid(body_id)
    elif body_id > 1000000:
        body = Comet(body_id)
    elif body_id > 1000:
        body = Body(body_id)
    elif body_id > 10:
        if body_id % 100 == 99:
            body = Planet(body_id)
        else:
            body = Satellite(body_id)
    elif body_id == 10:
        body = Body(10)
    elif body_id >= 0:
        body = Barycenter(body_id)
    elif body_id > -1000:
        body = Spacecraft(body_id)
    elif body_id >= -100000:
        body = Instrument(body_id)
    else:
        body = Spacecraft(body_id)
    return body

### Helper ###
def _data_generator(name, times, ref_frame, abcorr, observer):
    for time in times:
        with ignored(spice.SpiceException):
            #TODO find correct exception
            #XXX good practice to ignore errors?
            yield [time] + list(spice.spkezr(name, Time.fromposix(time).et(),
                ref_frame, abcorr, observer)[0])

def _child_generator(start, stop):
    for i in xrange(start, stop):
        try:
            yield makebody(i)
        except ValueError: #XXX better check complete range?
            break


class Body(object):
    """Abstract base class"""

    _ABCORR = 'NONE'

    def __init__(self, body_id):
        _CACHE[body_id] = self #FIXME can lead to infinite loops when called too late in subclasses
        self._id = body_id
        self._name = spice.bodc2n(body_id)
        if self._name is None:
            raise ValueError('__init__() {} is not a valid option'.format(body_id))
        self._parent = None
        self._children = []

    def __str__(self):
        return self.__class__.__name__ + ' {} (ID {})'.format(self.name, self.id)

    def __repr__(self):
        return self.__class__.__name__ + '({})'.format(self.id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    def get_data(self, times, observer='SUN', ref_frame='ECLIPJ2000',
        abcorr=None):
        #TODO type checking
        #TODO conversion if observer is a Body
        if isinstance(times, numbers.Real):
            times = [float(real)]
        if isinstance(times, collections.Iterable):
            return numpy.array(tuple(_data_generator(self.name, times,
                ref_frame, abcorr or Body._ABCORR, observer))).transpose()
        msg = 'get_data() Real or Iterable argument expected, got {}'.format(type(times))
        raise TypeError(msg)

class Asteroid(Body):
    def __init__(self, body_id):
        super(Asteroid, self).__init__(body_id)

class Barycenter(Body):
    def __init__(self, body_id):
        super(Barycenter, self).__init__(body_id)

class Comet(Body):
    def __init__(self, body_id):
        super(Comet, self).__init__(body_id)

class Instrument(Body):
    def __init__(self, body_id):
        super(Instrument, self).__init__(body_id)
        spacecraft_id = self.id % 1000
        self._parent = makebody(spacecraft_id)

class Planet(Body):
    def __init__(self, body_id):
        super(Planet, self).__init__(body_id)
        self._parent = makebody(10)
        self._children = list(_child_generator(body_id - 98, body_id))

class Satellite(Body):
    def __init__(self, body_id):
        super(Satellite, self).__init__(body_id)
        self._parent = makebody(body_id - body_id % 100 + 99)

class Spacecraft(Body):
    def __init__(self, body_id):
        super(Spacecraft, self).__init__(body_id)
        self._children = list(_child_generator(body_id * 1000, body_id * 1000 + 1000))
