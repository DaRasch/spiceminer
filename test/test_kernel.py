#-*- coding:utf-8 -*-

import pytest

import random
import string
import itertools as itt

import spiceminer.kernel.lowlevel as lowlevel


def rstring(max_size):
    while True:
        yield ''.join(random.sample(string.lowercase, random.randint(1, max_size)))

def fnames():
    error = pytest.mark.xfail(raises=ValueError)
    rstrings = rstring(4)
    valid_ext = [''.join(ext) for ext in itt.product(('b', 't'), lowlevel.VALID_KERNEL_TYPES)]

    ### Valid
    for ext in valid_ext:
        # real file names
        yield '.'.join([next(rstrings), ext])
        # extension equals file name
        yield '.'.join([ext, ext])
        # multiple dots
        yield '...' + ext
        yield '.'.join(['.'.join(itt.islice(rstrings, 4)), ext])
        # no name
        yield '.' + ext

    ### Invalid
    # empty
    yield error('')
    yield error('.')
    # no extension
    yield error(next(rstrings) + '.')
    # no dot
    for ext in valid_ext:
        yield error(''.join([next(rstrings), ext]))
    # bad prefix
    for ext in valid_ext:
        yield error(''.join(['.', next(rstrings), ext]))
    # bad postfix
    for ext in valid_ext:
        yield error(''.join(['.', ext, next(rstrings)]))
    # blackbox
    for rstr in itt.islice(rstrings, 4):
        if rstr not in valid_ext:
            yield error('.' + rstr)


class TestLowlevel:
    @pytest.mark.parametrize('filename', fnames())
    def test_filter_extension(self, filename):
        assert lowlevel.filter_extensions(filename) in lowlevel.VALID_KERNEL_TYPES

    def test_load_any(self):
        pass

    def test_unload_any(self):
        pass

class TestHighlevel:
    def test_load(self):
        pass

    def test_load_single(self):
        pass

    def test_unload(self):
        pass

