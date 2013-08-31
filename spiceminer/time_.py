#!/usr/bin/env python
#-*- coding:utf-8 -*-

import functools
import numbers
import time
import calendar
import datetime

import spiceminer._spicewrapper as spice

__all__ = ['Time']


### Helpers for argument checking ###
def _argcheck_basic(min_, max_, name, value):
    if not isinstance(value, int):
        msg = '__init__() {}: Integer argument expected, got {}'
        raise TypeError(msg.format(name, type(value)))
    if not (min_ <= value <= max_):
        msg = '__init__() {} must be in {}..{}'
        raise ValueError(msg.format(name, min_, max_))

def _argcheck_day(day, month, year):
    if not isinstance(day, int):
        msg = '__init__() day: Integer argument expected, got {}'
        raise TypeError(msg.format(type(day)))
    if not 1 <= day <= calendar.monthrange(year, month)[1]:
        msg = '__init__() day must be in 1..{}'
        raise ValueError(msg.format(calendar.monthrange(year, month)[1]))

def _argcheck_second(second):
    if not isinstance(second, numbers.Real):
        msg = '__init__() second: int or float argument expected, got {}'
        raise TypeError(msg.format(type(second)))
    if not 0 <= second < 60:
        msg = '__init__() 0 <= second < 60 expected, got {}'
        raise ValueError(msg.format(second))


@functools.total_ordering
class Time(numbers.Real):
    _ARGCHECKS = [
        ('year', lambda x, y, z: _argcheck_basic(1900, 9999, 'year', x)),
        ('month', lambda x, y, z: _argcheck_basic(1, 12, 'month', x)),
        ('day', lambda x, y, z: _argcheck_day(x, y, z)),
        ('hour', lambda x, y, z: _argcheck_basic(0, 23, 'hour', x)),
        ('minute', lambda x, y, z: _argcheck_basic(0, 59, 'minute', x)),
        ('second', lambda x, y, z: _argcheck_second(x))]

    def __init__(self, year=1970, month=1, day=1, hour=0, minute=0, second=0):
        super(Time, self).__init__()
        mapping = locals()
        #print mapping
        for name, func in Time._ARGCHECKS:
            value = mapping[name]
            func(value, month, year)
        self._value = calendar.timegm([year, month, day, hour, minute, 0, 0, 0,
            -1]) + second

    ### Additional constructors ###
    @classmethod
    def fromposix(cls, t):
        tmp = time.gmtime(t)
        tmpfuncs , Time._ARGCHECKS = Time._ARGCHECKS, {} # Hax! to avoid unnecessary type checking
        instance = cls(*tmp[:5], second=tmp[5] + (t - int(t)))
        Time._ARGCHECKS = tmpfuncs
        return instance

    @classmethod
    def fromydoy(cls, year, doy):
        if not doy < 364 + calendar.isleap(year):
            raise ValueError('fromydoy() doy out of range, got {}'.format(doy))
        seconds = doy * 86400
        new = cls(year)
        new._value += seconds
        return new

    @classmethod
    def fromdatetime(cls, dt):
        tmpfuncs , Time._ARGCHECKS = Time._ARGCHECKS, {} # Hax! to avoid unnecessary type checking
        instance = cls(*dt.utctimetuple()[:5],
            second=dt.second + dt.microsecond / 1000.0)
        Time._ARGCHECKS = tmpfuncs

    ### Real-type stuff###
    @property
    def real(self):
        return float(self._value)

    def __float__(self):
        return float(self._value)

    ### Comparisons ###
    #Supported: int, float, complex, datetime, date
    def __eq__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real == calendar.timegm(other.utctimetuple())
        if isinstance(other, datetime.date):
            return self.real == calendar.timegm(other.utctimetuple())
        try:
            return self.real == float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real < calendar.timegm(other.utctimetuple())
        if isinstance(other, datetime.date):
            return self.real < calendar.timegm(other.utctimetuple())
        try:
            return self.real < float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real <= calendar.timegm(other.utctimetuple())
        if isinstance(other, datetime.date):
            return self.real <= calendar.timegm(other.utctimetuple())
        try:
            return self.real <= float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    ### Math ###
    def __abs__(self):
        new = Time()
        new._value = abs(self.real)
        return new

    def __neg__(self):
        new = Time()
        new._value = self.real * -1
        return new

    def __pos__(self):
        new = Time()
        new._value = self.real
        return new

    def __trunc__(self):
        new = Time()
        new._value = self.real.__trunc__()
        return new

    ### Self is left operand ###
    #Supported: int, float
    def __add__(self, other):
        if isinstance(other, Time):
            return NotImplemented
        if isinstance(other, numbers.Real):
            new = Time()
            new._value = self.real + other.real
            return new
        return NotImplemented

    def __sub__(self, other): #XXX allow sub with datetime or timedelta?
        if isinstance(other, Time):
            return self.real - other.real
        if isinstance(other, numbers.Real):
            new = Time()
            new._value = self.real - other.real
            return new
        return NotImplemented

    def __mul__(self, other):
        return NotImplemented
    def __div__(self, other):
        return NotImplemented
    def __truediv__(self, other):
        return NotImplemented
    def __mod__(self, other):
        return NotImplemented
    def __floordiv__(self, other):
        return NotImplemented
    def __pow__(self, other):
        return NotImplemented

    ### Self is right operand ###
    def __radd__(self, other): #XXX should returntype be Time?
        try:
            return self.real + other
        except ValueError:
            return NotImplemented

    def __rmul__(self, other):
        return NotImplemented
    def __rdiv__(self, other):
        return NotImplemented
    def __rtruediv__(self, other):
        return NotImplemented
    def __rmod__(self, other):
        return NotImplemented
    def __rfloordiv__(self, other):
        return NotImplemented
    def __rpow__(self, other):
        return NotImplemented

    ### Representation ###
    def __str__(self):
        fraction = float(self) - int(self.real)
        return time.strftime("%Y-%m-%dT%H:%M:%S.",self.timetuple()) + str(fraction)[2:]

    def __repr__(self):
        tmp = self.timetuple()
        argstr = '(year={1}, month={2}, day={3}, hour={4}, minute={5}, second={0})'
        return self.__class__.__name__ + argstr.format(tmp[5] + self.real - int(self.real), *tmp[:5])

    ### Protected fields ###
    @property
    def year(self):
        return self.timetuple()[0]
    @property
    def month(self):
        return self.timetuple()[1]
    @property
    def day(self):
        return self.timetuple()[2]
    @property
    def hour(self):
        return self.timetuple()[3]
    @property
    def minute(self):
        return self.timetuple()[4]
    @property
    def second(self):
        return self.timetuple()[5] + (self.real - int(self.real))
    @property
    def doy(self):
        tmp = self.timetuple()
        fraction = (tmp[3] * 3600 + tmp[4] * 60 + tmp[5] + (self.real - int(self.real))) / 86400.0
        return tmp[7] + fraction

    ### Additional methods ###
    def timetuple(self):
        return time.gmtime(self.real)

    def et(self):
        return self.real - 946728000 - spice.deltet(self, 'UTC')

    def tai(self):
        return spice.unitim(self.et(), 'ET', 'TAI')

    def tdb(self):
        return spice.unitim(self.et(), 'ET', 'TDB')

    def tdt(self):
        return spice.unitim(self.et(), 'ET', 'TDT')

    def jdtdb(self):
        return spice.unitim(self.et(), 'ET', 'JDTDB')

    def jdtdt(self):
        return spice.unitim(self.et(), 'ET', 'JDTDT')

    def jed(self):
        return spice.unitim(self.et(), 'ET', 'JED')
