#-*- coding:utf-8 -*-

import pytest


import datetime as dt

import numpy as np

from spiceminer import extra

def test_angle():
    x = np.array([1, 0, 0])
    y = np.array([0, 1, 0])
    assert extra.angle(x, y) == np.pi / 2
    assert extra.angle(x, x) == 0.0
    assert extra.angle(x, -x) == np.pi

def test_frange():
    with pytest.raises(TypeError):
        extra.frange()
    with pytest.raises(TypeError):
        extra.frange(0, 8, 2, 4)
    with pytest.raises(ValueError):
        extra.frange('a')
    with pytest.raises(TypeError):
        extra.frange(None)
    assert list(extra.frange(0)) == []
    assert list(extra.frange(8, 0)) == []
    assert list(extra.frange(0, 8, -1)) == []
    assert list(extra.frange(8, 0, -1)) == [8, 7, 6, 5, 4, 3, 2, 1]
    assert list(extra.frange(8.4)) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    assert list(extra.frange(4.8, 8.4)) == [4.8, 5.8, 6.8, 7.8]
    assert list(extra.frange(4.8, 8.4, 1.2)) == [4.8, 6.0, 7.2]
    assert list(extra.frange('0', '8', '2')) == [0, 2, 4, 6]

def test_dtrange():
    zero = dt.datetime(1970, 1, 1)
    eight = dt.datetime(1970, 1, 1, 0, 0, 8)
    eight_four = dt.datetime(1970, 1, 1, 0, 0, 8) + dt.timedelta(0, 0.4)
    print eight_four.microsecond
    four_eight = dt.datetime(1970, 1, 1, 0, 0, 4) + dt.timedelta(0, 0.8)
    neg_one = dt.timedelta(0, -1)
    one_two = dt.timedelta(0, 1.2)
    with pytest.raises(TypeError):
        extra.dtrange()
    with pytest.raises(TypeError):
        extra.dtrange(0, 8, 2, 4)
    with pytest.raises(AttributeError):
        extra.dtrange('a')
    with pytest.raises(TypeError):
        extra.frange(None)
    assert list(extra.dtrange(zero)) == []
    assert list(extra.dtrange(eight, zero)) == []
    assert list(extra.dtrange(zero, eight, neg_one)) == []
    assert list(extra.dtrange(eight, zero, neg_one)) == [8, 7, 6, 5, 4, 3, 2, 1]
    assert list(extra.dtrange(eight_four)) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    assert list(extra.dtrange(four_eight, eight_four)) == [4.8, 5.8, 6.8, 7.8]
    assert list(extra.dtrange(four_eight, eight_four, one_two)) == [4.8, 6.0, 7.2]
