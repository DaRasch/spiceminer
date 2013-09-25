#-*- coding:utf-8 -*-

import pytest


import datetime as dt

from spiceminer.time_ import Time


### Contructors ###
def test_constructor_bounds():
    # year
    pytest.raises(ValueError, Time, year=0)
    assert Time(year=1) == -62135596800.0
    pytest.raises(ValueError, Time, year=10000)
    assert Time(year=9999) == 253370764800.0
    # month
    pytest.raises(ValueError, Time, month=0)
    assert Time(month=1) == 0.0
    pytest.raises(ValueError, Time, month=13)
    assert Time(month=12) == 28857600.0
    # day
    pytest.raises(ValueError, Time, day=0)
    assert Time(day=1) == 0.0
    pytest.raises(ValueError, Time, day=32)
    assert Time(day=31) == 2592000.0
    pytest.raises(ValueError, Time, month=2, day=29)
    assert Time(month=2, day=28) == 5011200.0
    # hour
    pytest.raises(ValueError, Time, hour=-1)
    assert Time(hour=0) == 0.0
    pytest.raises(ValueError, Time, hour=24)
    assert Time(hour=23) == 82800.0
    # minute
    pytest.raises(ValueError, Time, minute=-1)
    assert Time(minute=0) == 0.0
    pytest.raises(ValueError, Time, minute=60)
    assert Time(minute=59) == 3540.0
    # second
    pytest.raises(ValueError, Time, second=-0.1)
    assert Time(second=0) == 0.0
    pytest.raises(ValueError, Time, second=60)
    assert Time(second=59.9) == 59.9

def test_constructor_types():
    pytest.raises(TypeError, Time, year=0.1)
    pytest.raises(TypeError, Time, month=0.1)
    pytest.raises(TypeError, Time, day=0.1)
    pytest.raises(TypeError, Time, hour=0.1)
    pytest.raises(TypeError, Time, minute=0.1)
    pytest.raises(TypeError, Time, second='a')

def test_constructor_values():
    assert Time() == 0
    assert Time(2000, 1, 1) == 946684800
    assert Time(hour=22, minute=12, second=6.4568) == 79926.4568

def test_clsmeth_fromposix():
    pytest.raises(TypeError, Time.fromposix, None)
    assert Time.fromposix(0) == Time()

def test_clsmeth_fromydoy():
    pytest.raises(ValueError, Time.fromydoy, 2000, -0.1)
    pytest.raises(ValueError, Time.fromydoy, 2000, 365)
    pytest.raises(TypeError, Time.fromydoy, None, 200)
    assert Time.fromydoy(2000, 200) == Time(2000, 7, 19)

def test_clsmeth_fromdatetime():
    pytest.raises(AttributeError, Time.fromdatetime, None)
    assert Time.fromdatetime(dt.datetime(2000, 1, 1) + dt.timedelta(0, 0.4)) == Time(2000, second=0.4)


### Comparisons ###
@pytest.fixture(scope='module')
def times():
    return (Time(), Time(2000), dt.datetime(1970, 1, 1),
        dt.datetime(2000, 1, 1), dt.date(1970, 1, 1), dt.date(2000, 1, 1))

def test_eq(times):
    time, dtime, ddate = times[::2]
    assert time == Time()
    assert time == dtime
    assert dtime == time
    assert time == ddate
    assert ddate == time

def test_lt(times):
    time0, time1, dtime0, dtime1, ddate0, ddate1 = times
    assert time0 < time1
    assert time0 < dtime1
    assert dtime0 < time1
    assert time0 < ddate1
    assert ddate0 < time1
