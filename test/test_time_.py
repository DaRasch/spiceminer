#!/usr/bin/env python
#-*- coding:utf-8 -*-
import datetime as dt

import nose.tools as tools

from spiceminer.time_ import Time


def test_constructor_valid():
    assert Time() == 0
    assert Time(2000, 1, 1) == 946684800
    assert Time(hour=22, minute=12, second=6.4568) == 79926.4568

def test_bounds_valid_year():
    assert Time(year=1900) == -2208988800.0
    assert Time(year=9999) == 253370764800.0

def test_bounds_valid_month():
    assert Time(month=1) == 0.0
    assert Time(month=12) == 28857600.0

def test_bounds_valid_day():
    assert Time(day=1) == 0.0
    assert Time(day=30) == 2505600.0

def test_bounds_valid_hour():
    assert Time(hour=0) == 0.0
    assert Time(hour=23) == 82800.0

def test_bounds_valid_minute():
    assert Time(minute=0) == 0.0
    assert Time(minute=59) == 3540.0

def test_bounds_valid_second():
    assert Time(second=0) == 0.0
    assert Time(second=59.9999999) == 59.9999999

@tools.raises(ValueError)
def test_bounds_fail_year_0():
    Time(year=1899)
@tools.raises(TypeError)
def test_bounds_fail_year_float():
    Time(year=0.1)
@tools.raises(ValueError)
def test_bounds_fail_year_10000():
    Time(year=10000)
@tools.raises(ValueError)
def test_bounds_fail_month_0():
    Time(month=0)
@tools.raises(TypeError)
def test_bounds_fail_month_float():
    Time(month=0.1)
@tools.raises(ValueError)
def test_bounds_fail_month_13():
    Time(month=13)
@tools.raises(ValueError)
def test_bounds_fail_day_0():
    Time(day=0)
@tools.raises(TypeError)
def test_bounds_fail_day_float():
    Time(day=0.1)
@tools.raises(ValueError)
def test_bounds_fail_day_32():
    Time(day=32)
@tools.raises(ValueError)
def test_bounds_fail_hour_negative():
    Time(hour=-1)
@tools.raises(TypeError)
def test_bounds_fail_hour_float():
    Time(hour=0.1)
@tools.raises(ValueError)
def test_bounds_fail_hour_24():
    Time(hour=24)
@tools.raises(ValueError)
def test_bounds_fail_minute_negative():
    Time(minute=-1)
@tools.raises(TypeError)
def test_bounds_fail_minute_float():
    Time(minute=0.1)
@tools.raises(ValueError)
def test_bounds_fail_minute_60():
    Time(minute=60)
@tools.raises(ValueError)
def test_bounds_fail_second_negative():
    Time(second=-0.1)
@tools.raises(ValueError)
def test_bounds_fail_second_60():
    Time(second=60)
@tools.raises(TypeError)
def test_bounds_fail_second_str():
    Time(second='60')

def test_clsmeth_fromposix_valid():
    assert Time.fromposix(0) == Time()

def test_clsmeth_fromydoy_valid():
    assert Time.fromydoy(2000, 200) == Time(2000, 7, 19)

def test_clsmeth_fromdatetime_valid():
    assert Time.fromdatetime(dt.datetime(2000, 1, 1)) == Time(2000)
