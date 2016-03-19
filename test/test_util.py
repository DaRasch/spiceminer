#-*- coding:utf-8 -*-

import pytest

import os
import collections
import itertools as itt

import spiceminer.util as util


def gen_ignored():
    yield (Exception,)
    yield (ValueError, TypeError)
    yield (KeyError, IndexError, AttributeError)

@pytest.mark.parametrize('errors', gen_ignored())
def test_ignored(errors):
    for error in errors:
        with util.ignored(*errors):
            raise error()


iterable_paths = ['.', '..', __file__]
cleanable_paths = [
    '~',
    '$ENV_TEST',
    '$ENV_TEST/..',
    pytest.mark.xfail(raises=AssertionError)('/..')
]

@pytest.mark.parametrize('path', iterable_paths + cleanable_paths)
def test_cleanpath(path, monkeypatch):
    monkeypatch.setenv('ENV_TEST', '.')
    path = util.cleanpath(path)
    assert os.path.exists(path)
    for symbol in ['~', '$', '{', '}', '..']:
        assert symbol not in path


@pytest.mark.parametrize('path', iterable_paths)
@pytest.mark.parametrize('recursive', [True, False])
@pytest.mark.parametrize('followlinks', [True, False])
def test_iterable_path(path, recursive, followlinks):
    iterable = util.iterable_path(path, recursive, followlinks)
    assert isinstance(iterable, collections.Iterable)
    for dir_path, dirs, files in itt.islice(iterable, 5):
        assert os.path.exists(dir_path)
        for fname in files:
            assert os.path.exists(os.path.join(dir_path, fname))


def gen_basics():
    yield pytest.mark.xfail(raises=TypeError)(([1], []))
    yield pytest.mark.xfail(raises=ValueError)(([(1,)], []))
    yield pytest.mark.xfail(raises=ValueError)(([(1, 2, 3)], []))
    yield [], []
    yield [(1, 2), (1, 2)], [(1, 2)]
    yield [(1, 2), (2, 3)], [(1, 3)]
    yield [(1, 2), (3, 4)], [(1, 2), (3, 4)]
    yield [(1, 3), (2, 4)], [(1, 4)]
    yield zip(range(0, 100, 5), range(5, 101, 5)), [(0, 100)]

def gen_infix():
    # equivalence
    yield [], [], True, [], []
    yield [(1, 2), (2, 3)], [(1, 3)], True, [(1, 3)], [(1, 3)]
    # addition
    yield [(1, 2)], [(2, 3)], False, [(1, 3)], [(1, 2)]
    yield [(2, 3)], [(1, 2)], False, [(1, 3)], [(2, 3)]
    yield [(1, 2), (3, 4)], [(2, 3)], False, [(1, 4)], [(1, 2), (3, 4)]
    # subtraction
    yield [(1, 2), (2, 3)], [(1, 2)], False, [(1, 3)], [(2, 3)]

class TestTimeWindows:
    @pytest.mark.parametrize('args,merged', gen_basics())
    def test_basics(self, args, merged):
        # init
        instance = util.TimeWindows(*args)
        assert instance._merged == merged
        # properties
        assert instance.raw == args
        assert instance.raw is not instance._raw
        # sequence behavior
        assert instance[:] == merged
        try:
            assert len(instance) == len(merged)
            assert instance[0] == merged[0]
            assert merged[0] in instance
        except IndexError:
            pass
        assert list(iter(instance)) == merged
        assert list(reversed(instance)) == merged[::-1]

    @pytest.mark.parametrize('args1,args2,equal,add,sub', gen_infix())
    def test_infix_methods(self, args1, args2, equal, add, sub):
        instance_0 = util.TimeWindows(*args1)
        instance_1 = util.TimeWindows(*args2)
        assert (instance_0 == instance_1) is equal
        assert (instance_0 + instance_1) == add
        assert (instance_0 - instance_1) == sub
        tmp = instance_0
        assert tmp is instance_0
        tmp += instance_1
        assert tmp is not instance_0

