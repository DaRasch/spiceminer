#!/usr/bin/env python
#-*- coding:utf-8 -*-

import functools
import numbers
import time
import calendar
import datetime

import spice

__all__ = ['Time']


@functools.total_ordering
class Time(numbers.Real):
    def __init__(self, year=1970, month=1, day=1, hour=0, minute=0, second=0):
        super(Time, self).__init__()
        #TODO allow kwargs
        #TODO check arg ranges
        self._value = calendar.timegm([year, month, day, hour, minute, 0, 0, 0,
            -1]) + second

    ### Additional constructors ###
    @classmethod
    def fromposix(cls, t):
        tmp = time.gmtime(t)
        return cls(*tmp[:5], second=tmp[5] + (t - int(t)))

    @classmethod
    def fromydoy(cls, year, doy):
        seconds = doy * 86400
        new = cls(year)
        new._value += seconds
        return new

    @classmethod
    def fromdatetime(cls, dt):
        return cls(*dt.utctimetuple()[:5], second=dt.second + dt.microsecond / 1000.0)

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
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real < calendar.timegm(other.utctimetuple())
        if isinstance(other, datetime.date):
            return self.real < calendar.timegm(other.utctimetuple())
        try:
            return self.real < float(other)
        except AttributeError:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real <= calendar.timegm(other.utctimetuple())
        if isinstance(other, datetime.date):
            return self.real <= calendar.timegm(other.utctimetuple())
        try:
            return self.real <= float(other)
        except AttributeError:
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
        if isinstance(other, (numbers.Integral, numbers.Real)):
            new = Time()
            new._value = self.real + other.real
            return new
        return NotImplemented

    def __sub__(self, other): #XXX allow sub with datetime or timedelta?
        if isinstance(other, Time):
            return self.real - other.real
        if isinstance(other, (numbers.Integral, numbers.Real)):
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
            return other + self.real
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
        return time.strftime("%Y-%m-%dT%H:%M:%S.", self.timetuple()) + str(fraction)[2:]

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
    def day_of_year(self):
        tmp = self.timetuple()
        fraction = (tmp[3] * 3600 + tmp[4] * 60 + tmp[5] + (self.real - int(self.real))) / 86400.0
        return tmp[7] + fraction

    ### Additional methods ###
    def timetuple(self):
        return time.gmtime(self.real)

    def et(self):
        return spice.utc2et(str(self))

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
