#!/usr/bin/env python
#-*- coding:utf-8 -*-

import nose.tools as tools

from spiceminer.time_ import Time


def test_init_valid():
    tools.assert_equals(Time(), 0)
    tools.assert_equals(Time(2000, 1, 1), 946684800)
    tools.assert_equals(Time(hour=22, minute=12, second=6.4568), 79926.4568)

@tools.raises(ValueError)
def test_init_fail_year_0():
    Time(year=0)
@tools.raises(TypeError)
def test_init_fail_year_float():
    Time(year=0.1)
@tools.raises(ValueError)
def test_init_fail_year_10000():
    Time(year=10000)
@tools.raises(ValueError)
def test_init_fail_month_0():
    Time(month=0)
@tools.raises(TypeError)
def test_init_fail_month_float():
    Time(month=0.1)
@tools.raises(ValueError)
def test_init_fail_month_13():
    Time(month=13)
@tools.raises(ValueError)
def test_init_fail_day_0():
    Time(day=0)
@tools.raises(TypeError)
def test_init_fail_day_float():
    Time(day=0.1)
@tools.raises(ValueError)
def test_init_fail_day_32():
    Time(day=32)
@tools.raises(ValueError)
def test_init_fail_hour_negative():
    Time(hour=-1)
@tools.raises(TypeError)
def test_init_fail_hour_float():
    Time(hour=0.1)
@tools.raises(ValueError)
def test_init_fail_hour_24():
    Time(hour=24)
@tools.raises(ValueError)
def test_init_fail_minute_negative():
    Time(minute=-1)
@tools.raises(TypeError)
def test_init_fail_minute_float():
    Time(minute=0.1)
@tools.raises(ValueError)
def test_init_fail_minute_60():
    Time(minute=60)
@tools.raises(ValueError)
def test_init_fail_second_negative():
    Time(second=-0.1)
@tools.raises(ValueError)
def test_init_fail_second_60():
    Time(second=60)
@tools.raises(ValueError, TypeError)
def test_init_fail_second_str():
    Time(second='60')
