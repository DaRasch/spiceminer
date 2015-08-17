#-*- coding:utf-8 -*-

import pytest

import random
import string
import itertools as itt

import spiceminer as sm
import spiceminer.kernel.lowlevel as lowlevel


def generate_strings(max_size):
    while True:
        yield ''.join(random.sample(string.lowercase, random.randint(1, max_size)))

def generate_filenames():
    xfail = pytest.mark.xfail(raises=ValueError)
    rstrings = generate_strings(4)
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
    yield xfail('')
    yield xfail('.')
    # no extension
    yield xfail(next(rstrings) + '.')
    # only extension
    for ext in valid_ext:
        yield xfail(ext)
    # no dot
    for ext in valid_ext:
        yield xfail(''.join([next(rstrings), ext]))
    # bad prefix
    for ext in valid_ext:
        yield xfail(''.join(['.', next(rstrings), ext]))
    # bad postfix
    for ext in valid_ext:
        yield xfail(''.join(['.', ext, next(rstrings)]))
    # blackbox
    for rstr in itt.islice(rstrings, 4):
        if rstr not in valid_ext:
            yield xfail('.' + rstr)

@pytest.mark.parametrize('filename', generate_filenames())
def test_filter_extensions(filename):
    assert lowlevel.filter_extensions(filename) in lowlevel.VALID_KERNEL_TYPES


def test_load_any(kernelfile):
    info, time_window_map = lowlevel.load_any(*kernelfile)
    assert info in ['pos', 'rot', 'none']
    assert isinstance(time_window_map, dict)

@pytest.mark.parametrize('path', ['.', '/', '~'])
def test_load_any_errors(path):
    with pytest.raises(IOError):
        info, time_window_map = lowlevel.load_any(path, '')


def test_unload_any():
    pass


# misc
@pytest.mark.parametrize('path', ['.'])
def test_load_dummy(path):
    assert lowlevel._load_dummy(path) == ('none', {})

def _abstract_loader_fixture(request, kernelfile, types):
    if kernelfile.type in types:
        return kernelfile.path
    else:
        request.applymarker(pytest.mark.xfail(raises=sm.SpiceError))
        return kernelfile.path

# sp
@pytest.fixture
def sp_file(request, kernelfile):
    return _abstract_loader_fixture(request, kernelfile, ['sp'])

@pytest.mark.usefixtures('with_leapseconds')
def test_load_sp(sp_file):
    info_type, time_window_map = lowlevel._load_sp(sp_file)
    assert info_type == 'pos'
    assert time_window_map != {}

# c/sc
@pytest.fixture
def c_file(request, kernelfile):
    return _abstract_loader_fixture(request, kernelfile, ['c', 'sc'])

@pytest.mark.usefixtures('with_leapseconds')
def test_load_c(c_file):
    info_type, time_window_map = lowlevel._load_c(c_file)
    assert info_type == 'rot'
    assert time_window_map != {}

# pc
@pytest.fixture
def pc_file(request, kernelfile):
    return _abstract_loader_fixture(request, kernelfile, ['pc'])

@pytest.mark.usefixtures('with_leapseconds')
def test_load_pc(pc_file):
    info_type, time_window_map = lowlevel._load_pc(pc_file)
    assert info_type == 'rot'
    assert time_window_map != {}

# pc
@pytest.fixture
def f_file(request, kernelfile):
    return _abstract_loader_fixture(request, kernelfile, ['f'])

@pytest.mark.usefixtures('with_leapseconds')
def test_load_f(f_file):
    info_type, time_window_map = lowlevel._load_f(f_file)
    assert info_type == 'pos'
    assert time_window_map != {}
