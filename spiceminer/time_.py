#-*- coding:utf-8 -*-

import functools
import numbers
import time
import calendar
import datetime

from contextlib import contextmanager

import spiceminer._spicewrapper as spice

__all__ = ['Time']


### Miscellaneuos helpers ###
@contextmanager
def _no_argcheck():
    '''Hax! Avoid unnecessary type checking.
    Used for alternate constructors which do their own type checking.
    '''
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
    a subclass of ``numbers.Real``, so it acts like a float in mathematical
    operations.

    Comparison operations also support datetime objects.

    Addition and subtraction operations yield new Time objects when the left
    operand is already a Time object. They also support timedelta objects as
    right operands.

    Parameters
    ----------
    year: int, optional
        [1..9999]
    month: int, optional
        [1..12]
    day: int, optional
        [1..31]
    hour: int, optional
        [0..23]
    minute: int, optional
        [0..59]
    second: float, optional
        [0..60)

    Raises
    ------
    ValueError
        If an argument is out of bounds.
    TypeError
        If an argument has the wrong type.

    Attributes
    ----------
    *classattribute* MINUTE: float
        One minute in seconds
    *classattribute* HOUR: float
        One hour in seconds
    *classattribute* DAY: float
        One day in seconds
    *classattribute* WEEK: float
        One week (7 days) in seconds
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: float

    Examples
    --------
    >>> Time()
    Time(year=1970, month=1, day=1, hour=0, minute=0, second=0)
    >>> Time(2000, 5, hour=14)
    Time(year=2000, month=5, day=1, hour=14, minute=0, second=0)
    '''

    _ARGCHECKS = [
        ('year', lambda x, y, z: _argcheck_basic(1, 9999, 'year', x)),
        ('month', lambda x, y, z: _argcheck_basic(1, 12, 'month', x)),
        ('day', lambda x, y, z: _argcheck_day(x, y, z)),
        ('hour', lambda x, y, z: _argcheck_basic(0, 23, 'hour', x)),
        ('minute', lambda x, y, z: _argcheck_basic(0, 59, 'minute', x)),
        ('second', lambda x, y, z: _argcheck_second(x))]

    MINUTE = 60.0
    HOUR = 60.0 * MINUTE
    DAY = 24.0 * HOUR
    WEEK = 7.0 * DAY

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
    def now(cls):
        '''Get current time.

        Returns
        -------
        Time
            New POSIX timestamp.
        '''
        return cls.fromdatetime(datetime.utcnow())

    @classmethod
    def fromposix(cls, timestamp):
        '''Generate a Time instance from a single number.

        Allows sub second precision.

        Parameters
        ----------
        timestamp: float
            A number representing a POSIX/UNIX timestamp.

        Returns
        -------
        Time
            New POSIX timestamp.
        '''
        with _no_argcheck():
            instance = cls(second=float(timestamp))
        return instance

    @classmethod
    def fromstring(cls, string, format='%Y-%m-%d %H:%M:%S'):
        '''Equivalent to time.strptime().

        Does not allow sub second precision.

        Parameters
        ----------
        string: str
            The string to parse.
        format: The format of the string.

        Returns
        -------
        Time
            New POSIX timestamp.
        '''
        return cls.fromposix(calendar.timegm(time.strptime(string, format)))

    @classmethod
    def fromydoy(cls, year, doy):
        '''Generate a Time instance from two numbers representing a year and a
        day in that year.

        Allows sub second precision.

        Parameters
        ----------
        year: int
            The year to convert.
        doy: float
            The day od year to convert. Can be a ``float`` to allow for
            hour, minute, etc. measurement.

        Returns
        -------
        Time
            New POSIX timestamp.

        Raises
        ------
        ValueError
            If ``0 <= doy < (365 or 366)``
        '''
        if not 0 <= doy < 365 + calendar.isleap(year):
            msg = 'fromydoy() doy out of range, got {}'
            raise ValueError(msg.format(doy))
        seconds = float(doy) * cls.DAY
        with _no_argcheck():
            instance = cls(int(year), second=seconds)
        return instance

    @classmethod
    def fromdatetime(cls, dt):
        '''Generate a Time instance from a datetime object.

        Allows sub second precision.

        Parameters
        ----------
        dt: datetime
            The datetime object to convert.

        Returns
        -------
        Time
            New POSIX timestamp.
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
        return float(self._value)

    def __float__(self):
        return float(self._value)

    ### Comparisons ###
    #Supported: int, float, datetime, date, Time
    def __eq__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real == self.__class__.fromdatetime(other).real
        if isinstance(other, datetime.date):
            return self.real == calendar.timegm(other.timetuple())
        if isinstance(other, numbers.Real):
            return self.real == other.real
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, datetime.datetime):
            return self.real < self.__class__.fromdatetime(other).real
        if isinstance(other, datetime.date):
            return self.real < calendar.timegm(other.timetuple())
        if isinstance(other, numbers.Real):
            return self.real < other.real
        return NotImplemented

    def __le__(self, other):
        return self < other or self == other

    ### Math ###
    def __abs__(self):
        return abs(self.real)

    def __neg__(self):
        return -self.real

    def __pos__(self):
        return +self.real

    def __trunc__(self):
        return self.real.__trunc__()

    ### Self is left operand ###
    #Supported: int, float, timedelta, Time
    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            with _no_argcheck():
                new = Time(second=self.real + other.total_seconds())
            return new
        if isinstance(other, numbers.Real):
            with _no_argcheck():
                new = Time(second=self.real + other.real)
            return new
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, datetime.timedelta):
            with _no_argcheck():
                new = Time(second=self.real + other.total_seconds())
            return new
        if isinstance(other, numbers.Real):
            with _no_argcheck():
                new = Time(second=self.real - float(other))
            return new
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return self.real * other.real
        return NotImplemented
    def __div__(self, other):
        if isinstance(other, numbers.Real):
            return self.real / other.real
        return NotImplemented
    def __truediv__(self, other):
        if isinstance(other, numbers.Real):
            return self.real / other.real
        return NotImplemented
    def __mod__(self, other):
        if isinstance(other, numbers.Real):
            return self.real % other.real
        return NotImplemented
    def __floordiv__(self, other):
        if isinstance(other, numbers.Real):
            return self.real // other.real
        return NotImplemented
    def __pow__(self, other):
        if isinstance(other, numbers.Real):
            return self.real ** other.real
        return NotImplemented

    ### Self is right operand ###
    def __radd__(self, other):
        if isinstance(other, numbers.Real):
            return other.real + self.real
        return NotImplemented
    def __rmul__(self, other):
        if isinstance(other, numbers.Real):
            return other.real * self.real
        return NotImplemented
    def __rdiv__(self, other):
        if isinstance(other, numbers.Real):
            return other.real / self.real
        return NotImplemented
    def __rtruediv__(self, other):
        if isinstance(other, numbers.Real):
            return other.real / self.real
        return NotImplemented
    def __rmod__(self, other):
        if isinstance(other, numbers.Real):
            return other.real % self.real
        return NotImplemented
    def __rfloordiv__(self, other):
        if isinstance(other, numbers.Real):
            return other.real // self.real
        return NotImplemented
    def __rpow__(self, other):
        if isinstance(other, numbers.Real):
            return other.real ** self.real
        return NotImplemented

    ### Representation ###
    def __str__(self):
        args = self.timetuple()
        date = '-'.join(str(x).zfill(2) for x in args[:3])
        time_ = ':'.join(str(x).zfill(2) for x in args[3:6])
        fraction = str(self.real - int(self))[1:]
        if self < 0:
            fraction = fraction[1:]
        return '{} {}{} UTC'.format(date, time_, fraction[:3])

    def __repr__(self):
        args = list(self.timetuple())
        fraction = str(self.real - int(self))[1:]
        if self < 0:
            fraction = fraction[1:]
        argstr = '(year={}, month={}, day={}, hour={}, minute={}, second={}{})'
        argstr = argstr.format(*(args[:6] + [fraction[:3]]))
        return self.__class__.__name__ + argstr

    def __format__(self, fmt):
        fraction = fmt.replace('%f', str(self.real - int(self.real))[2:])
        return time.strftime(fraction, self.timetuple())

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
        fraction = self.real - int(self)
        return self.timetuple()[5] + fraction

    ### Additional methods ###
    def day_of_year(self):
        '''The day of year including hours, minutes, and seconds.

        Allows sub second precision.

        Returns
        -------
        float
            Day of the year.
        '''
        args = self.timetuple()
        seconds = args[3] * 3600 + args[4] * 60 + args[5]
        fraction = self.real - int(self)
        return args[7] + (seconds + fraction) / 86400.0

    def week_of_year(self):
        '''The week of year including days, hours, minutes, and seconds.

        Allows sub second precision.

        Returns
        -------
        float
            Week of the year.
        '''
        args = self.timetuple()
        week = args[7] / 7.0
        seconds = args[3] * 3600 + args[4] * 60 + args[5]
        fraction = self.real - int(self)
        return week + (seconds + fraction) / self.__class__.WEEK

    def timetuple(self):
        '''Struct representation as produced by ``time.gmtime()``.

        Does not allow sub second precision.

        Returns
        -------
        time_struct
            Time representation used by some other time related functions.
        '''
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
