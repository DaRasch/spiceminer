#-*- coding:utf-8 -*-

import pytest

import datetime as dt
import itertools as itt

import numpy as np

import spiceminer.extra as extra


def gen_angle():
    x, y, z = np.random.random((3, 3)) * np.identity(3) * 10
    # test orthogonal vectors
    for v0, v1 in itt.permutations((x, y, z), 2):
        yield v0, v1, np.pi / 2
    # test parallel vectors
    for v in (x, y, z, x + y, y + z, z + x):
        yield v, v, 0
        yield v, -v, np.pi

@pytest.mark.parametrize('v0, v1, expected', gen_angle())
def test_angle(v0, v1, expected):
    diff = 10e-5
    assert (expected - diff) < extra.angle(v0, v1) < (expected + diff)


def gen_frange():
    # errors
    yield pytest.mark.xfail(raises=TypeError)(([], None))
    yield pytest.mark.xfail(raises=TypeError)((np.random.random(4), None))
    yield pytest.mark.xfail(raises=TypeError)(([None], None))
    yield pytest.mark.xfail(raises=ValueError)((['None'], None))
    # 1 arg (stop)
    yield [-6], []
    yield [0], []
    yield [0.5], [0]
    yield [1], [0]
    yield [7], list(range(7))
    yield [3.5], [0, 1, 2 ,3]
    yield ['2.6'], [0, 1, 2]
    # 2 args (start, stop)
    yield [8, 0], []
    yield [-4, 0], list(range(-4 , 0))
    yield [0, 3], [0, 1, 2]
    yield [0, -9], []
    yield [0.5, 2.4], [0.5, 1.5]
    yield [3.7, 1.6], []
    # 3 args (start, stop, step)
    yield [4.8, 8.4, 1.2], [4.8, 6.0, 7.2]
    yield [8.4, 4.8, -1.2], [8.4, 7.2, 6.0]

@pytest.mark.parametrize('args,expected', gen_frange())
def test_range(args, expected):
    assert list(extra.frange(*args)) == expected

def gen_dtrange():
    zero = dt.datetime(1970, 1, 1)
    eight = dt.datetime(1970, 1, 1, 0, 0, 8)
    eight_four = dt.datetime(1970, 1, 1, 0, 0, 8) + dt.timedelta(0, 0.4)
    four_eight = dt.datetime(1970, 1, 1, 0, 0, 4) + dt.timedelta(0, 0.8)
    neg_one = dt.timedelta(0, -1)
    one_two = dt.timedelta(0, 1.2)
    yield pytest.mark.xfail(raises=TypeError)(([], None))
    yield pytest.mark.xfail(raises=TypeError)(([eight, zero, neg_one, one_two], None))
    yield pytest.mark.xfail(raises=TypeError)((['a'], None))
    yield pytest.mark.xfail(raises=TypeError)(([None], None))
    # 1 arg (stop)
    yield [neg_one], []
    yield [zero], []
    yield [one_two], [0, 1]
    yield [eight], list(range(8))
    # 2 args (start, stop)
    yield [eight, zero], []
    yield [neg_one, one_two], [-1, 0, 1]
    yield [zero, eight], list(range(8))
    yield [zero, neg_one], []
    yield [one_two, four_eight], [1.2, 2.4, 3.6]
    yield [four_eight, one_two], []
    # 3 args (start, stop, step)
    yield [four_eight, eight_four, one_two], [4.8, 6.0, 7.2]
    yield [eight_four, four_eight, neg_one], [8.4, 7.4, 6.4, 5.4]

@pytest.mark.parametrize('args,expected', gen_dtrange())
def test_dtrange(args, expected):
    assert list(extra.dtrange(*args)) == expected
