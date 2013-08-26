#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections
import numbers
import numpy

import spiceminer._spicewrapper as spice

from spiceminer.time_ import Time
from spiceminer._helpers import ignored

__all__ = ['Body']

### Helper ###
def _data_generator(name, times, ref_frame, abcorr, observer):
    for time in times:
        with ignored(spice.SpiceError): #XXX good practice to ignore errors?
            yield [time] + spice.spkezr(name, Time.fromposix(time).et(),
                ref_frame, abcorr, observer)[0]

def _child_generator(start, stop, step=1):
    for i in xrange(start, stop, step):
        with ignored(ValueError):
            yield Body(i)


class Body(object):
    """Abstract base class"""

    _CACHE = {}
    _ABCORR = 'NONE'

    def __new__(cls, body_id, *args, **kwargs):
        if not isinstance(body_id, numbers.Integral):
            msg = 'Body.__new__() integer argument expected, got {}'
            raise TypeError(msg.format(type(body_id)))
        ### factory function ###
        if body_id in Body._CACHE:
            body = Body._CACHE[body_id]
        elif body_id > 2000000:
            body = object.__new__(Asteroid, body_id, *args, **kwargs)
        elif body_id > 1000000:
            body = object.__new__(Comet, body_id, *args, **kwargs)
        elif body_id > 1000:
            body = object.__new__(cls, body_id, *args, **kwargs)
        elif body_id > 10:
            if body_id % 100 == 99:
                body = object.__new__(Planet, body_id, *args, **kwargs)
            else:
                body = object.__new__(Satellite, body_id, *args, **kwargs)
        elif body_id == 10:
            body = object.__new__(cls, 10, *args, **kwargs)
        elif body_id >= 0:
            body = object.__new__(Barycenter, body_id, *args, **kwargs)
        elif body_id > -1000:
            body = object.__new__(Spacecraft, body_id, *args, **kwargs)
        elif body_id >= -100000:
            body = object.__new__(Instrument, body_id, *args, **kwargs)
        else:
            body = object.__new__(Spacecraft, body_id, *args, **kwargs)
        return body

    def __init__(self, body_id):
        Body._CACHE[body_id] = self
        self._id = body_id
        self._name = spice.bodc2n(body_id)
        if self._name is None:
            msg = 'Body.__init__() {} is not a valid ID'
            raise ValueError(msg.format(body_id))

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
        return None
    @property
    def children(self):
        return []

    def get_data(self, times, observer='SUN', ref_frame='ECLIPJ2000',
        abcorr=None):
        if isinstance(observer, Body):
            observer = observer.name
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            return numpy.array(tuple(_data_generator(self.name, times,
                ref_frame, abcorr or Body._ABCORR, observer))).transpose()
        msg = 'get_data() Real or Iterable argument expected, got {}'
        raise TypeError(msg.format(type(times)))

    def get_pointing(self, times, observer='SUN', ref_frame='ECLIPJ2000',
        abcorr=None):
        if isinstance(observer, basestring):
            observer = Body(spice.bodn2c(observer))
        elif isinstance(observer, numbers.Real):
            observer = Body(observer)
        if isinstance(times, numbers.Real):
            times = [float(times)]
        if isinstance(times, collections.Iterable):
            for time in times:
                return spice.ckgp(self.id, observer.id, Time.fromposix(time).et() , 10000, ref_frame)


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

    @property
    def parent(self):
        offset = 0 if self.id % 1000 == 0 else -1
        spacecraft_id = self.id / 1000 + offset
        return Body(spacecraft_id)


class Planet(Body):
    def __init__(self, body_id):
        super(Planet, self).__init__(body_id)

    @property
    def parent(self):
        return Body(10)
    @property
    def children(self):
        return list(_child_generator(self.id - 98, self.id))


class Satellite(Body):
    def __init__(self, body_id):
        super(Satellite, self).__init__(body_id)

    @property
    def parent(self):
        return Body(self.id - self.id % 100 + 99)


class Spacecraft(Body):
    def __init__(self, body_id):
        super(Spacecraft, self).__init__(body_id)

    @property
    def children(self):
        return list(_child_generator(self.id * 1000, self.id * 1000 - 1000, -1))
