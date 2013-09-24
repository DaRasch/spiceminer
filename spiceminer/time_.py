#-*- coding:utf-8 -*-

import functools
import numbers
import time
import calendar
import datetime

from contextlib import contextmanager

import spiceminer._spicewrapper as spice

__all__ = ['Time']


### Miscelanuos helpers ###
@contextmanager
def _no_argcheck():
    # Hax! avoid unnecessary type checking
    _tmpfuncs, Time._ARGCHECKS = Time._ARGCHECKS, []
    try:
        yield
    finally:
        Time._ARGCHECKS = _tmpfuncs


### Helpers for argument checking ###
def _argcheck_basic(min_, max_, name, value):
    if not isinstance(value, numbers.Integral):
        msg = '__init__() {}: Integer argument expected, got {}'
        raise TypeError(msg.format(name, type(value)))
    if not (min_ <= value <= max_):
        msg = '__init__() {} must be in {}..{}'
        raise ValueError(msg.format(name, min_, max_))

def _argcheck_day(day, month, year):
    if not isinstance(day, numbers.Integral):
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
    '''A powerfull POSIX time representation that always references UTC. It is
    a subclass of ``numbers.Real``, so it acts like a float.

    :type year: ``int``
    :arg year: 1..9999
    :type month: ``int``
    :arg month: 1..12
    :type day: ``int``
    :arg day: 1..31
    :type hour: ``int``
    :arg hour: 0..23
    :type minute: ``int``
    :arg minute: 0..59
    :type second: ``float``
    :arg second: 0..<60
    :return: (:py:class:`~spiceminer.time_.Time`) -- New POSX timestamp.
    :raises:
      (``ValueError``) -- If an argument is out of bounds.

      (``TypeError``) -- If an argument has the wrong type.
    '''

    _ARGCHECKS = [
        ('year', lambda x, y, z: _argcheck_basic(1, 9999, 'year', x)),
        ('month', lambda x, y, z: _argcheck_basic(1, 12, 'month', x)),
        ('day', lambda x, y, z: _argcheck_day(x, y, z)),
        ('hour', lambda x, y, z: _argcheck_basic(0, 23, 'hour', x)),
        ('minute', lambda x, y, z: _argcheck_basic(0, 59, 'minute', x)),
        ('second', lambda x, y, z: _argcheck_second(x))]

    #: One minute in seconds.
    MINUTE = 60
    #: One hour in seconds.
    HOUR = 3600
    #: One day in seconds.
    DAY = 86400

    def __init__(self, year=1970, month=1, day=1, hour=0, minute=0, second=0):
        super(Time, self).__init__()
        args = locals()
        for name, func in Time._ARGCHECKS:
            value = args[name]
            func(value, month, year)
        self._value = calendar.timegm([year, month, day, hour, minute, 0, 0, 0,
            -1]) + second

    ### Additional constructors ###
    @classmethod
    def fromposix(cls, timestamp):
        '''Generate a :py:class:`~spiceminer.time_.Time` instance from a float.

        :type t: ``float``
        :arg t: A number representing a point in time.
        :return: (:py:class:`~spiceminer.time_.Time`) -- New POSIX timestamp.
        :raises: Nothing.
        '''
        with _no_argcheck():
            instance = cls(second=float(timestamp))
        return instance

    @classmethod
    def fromydoy(cls, year, doy):
        '''Generate a :py:class:`~spiceminer.time_.Time` instance from two
        numbers representing a year and a day in that year.

        :type year: ``int``
        :arg year: The year to convert.
        :type doy: ``float``
        :arg doy: The day od year to convert. Can be a ``float`` to allow for
          hour, minute, etc. measurement.

        :return: (:py:class:`~spiceminer.time_.Time`) -- New POSIX timestamp.
        :raises: (``ValueError``) -- If ``0 <= doy < (364 or 365)``
        '''
        if not 0 <= doy < 364 + calendar.isleap(year):
            msg = 'fromydoy() doy out of range, got {}'
            raise ValueError(msg.format(doy))
        seconds = float(doy) * 86400
        with _no_argcheck():
            instance = cls(int(year), second=seconds)
        return instance

    @classmethod
    def fromdatetime(cls, dt):
        '''Generate a :py:class:`~spiceminer.time_.Time` instance from a
        ``datetime`` object.

        :type dt: ``datetime``
        :arg dt: The object to convert.

        :return: (:py:class:`~spiceminer.time_.Time`) -- New POSIX timestamp.
        :raises: Nothing.
        '''
        with _no_argcheck():
            instance = cls(*dt.utctimetuple()[:5],
                second=dt.second + dt.microsecond / 1000000.0)
        return instance

    @classmethod
    def fromet(cls, et):
        et = float(et)
        with _no_argcheck():
            instance = cls(second=et + 946728000 + spice.deltet(et, 'UTC'))
        return instance

    ### Real-type stuff###
    @property
    def real(self):
        '''The value of the POSIX representation of an object. Required by the
        ``numbers.Real`` interface.
        '''
        return float(self._value)

    def __float__(self):
        return float(self._value)

    ### Comparisons ###
    #Supported: int, float, datetime, date, Time
    def __eq__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real == calendar.timegm(
                other.utctimetuple()) + (other.microsecond / 1000000.0)
        if isinstance(other, datetime.date):
            return self.real == calendar.timegm(other.timetuple())
        try:
            return self.real == float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real < calendar.timegm(
                other.utctimetuple()) + (other.microsecond / 1000000.0)
        if isinstance(other, datetime.date):
            return self.real < calendar.timegm(other.timetuple())
        try:
            return self.real < float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    def __le__(self, other):
        # TODO replace with __lt__ or __eq__
        if isinstance(other, datetime.datetime):
            return self.real <= calendar.timegm(
                other.utctimetuple()) + (other.microsecond / 1000000.0)
        if isinstance(other, datetime.date):
            return self.real <= calendar.timegm(other.timetuple())
        try:
            return self.real <= float(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    ### Math ###
    def __abs__(self):
        with _no_argcheck():
            new = Time(second=abs(self.real))
        return new

    def __neg__(self):
        with _no_argcheck():
            new = Time(second=-self.real)
        return new

    def __pos__(self):
        with _no_argcheck():
            new = Time(second=self.real)
        return new

    def __trunc__(self):
        return int(self.real)

    ### Self is left operand ###
    #Supported: int, float, timedelta, datetime, date, Time
    def __add__(self, other):
        if isinstance(other, Time):
            return NotImplemented
        if isinstance(other, datetime.timedelta):
            with _no_argcheck():
                new = Time(second=self.real + other.total_seconds())
            return new
        try:
            with _no_argcheck():
                new = Time(second=self.real + float(other))
            return new
        except TypeError:
            return NotImplemented
        except ValueError:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Time):
            return self.real - other.real
        if isinstance(other, datetime.datetime):
            return self.real - calendar.timegm(
                other.utctimetuple()) - (other.microsecond / 1000000.0)
        try:
            with _no_argcheck():
                new = Time(second=self.real - float(other))
            return new
        except TypeError:
            return NotImplemented
        except ValueError:
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
    def __radd__(self, other):
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
        args = self.timetuple()
        date = '-'.join(str(x).zfill(2) for x in args[:3])
        time_ = ':'.join(str(x).zfill(2) for x in args[3:6])
        fraction = str(self.real - int(self))[1:]
        if self < 0:
            fraction = fraction[1:]
        return '{}T{}{}'.format(date, time_, fraction[:3])

    def __repr__(self):
        args = list(self.timetuple())
        fraction = str(self.real - int(self))[1:]
        if self < 0:
            fraction = fraction[1:]
        argstr = '(year={}, month={}, day={}, hour={}, minute={}, second={}{})'
        argstr = argstr.format(*(args[:6] + [fraction[:3]]))
        return self.__class__.__name__ + argstr

    ### Protected fields ###
    @property
    def year(self):
        '''Year represented by the timestamp.'''
        return self.timetuple()[0]
    @property
    def month(self):
        '''Month represented by the timestamp.'''
        return self.timetuple()[1]
    @property
    def day(self):
        '''Day represented by the timestamp.'''
        return self.timetuple()[2]
    @property
    def hour(self):
        '''Hour represented by the timestamp.'''
        return self.timetuple()[3]
    @property
    def minute(self):
        '''Minute represented by the timestamp.'''
        return self.timetuple()[4]
    @property
    def second(self):
        '''Second represented by the timestamp.'''
        fraction = self.real - int(self)
        return self.timetuple()[5] + fraction
    @property
    def doy(self):
        '''Day of year represented by the timestamp.'''
        args = self.timetuple()
        seconds = args[3] * 3600 + args[4] * 60 + args[5]
        fraction = self.real - int(self)
        return args[7] + (seconds + fraction) / 86400.0

    ### Additional methods ###
    def timetuple(self):
        '''Struct representation as produced by ``time.gmtime()``.'''
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
