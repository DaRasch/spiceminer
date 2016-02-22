#-*- coding:utf-8 -*-

import pytest

import random
import string
import itertools as itt

import spiceminer as sm
import spiceminer.kernel.lowlevel as lowlevel


### Helpers ###
@pytest.fixture(scope='function', params=['pos', 'rot', 'none'])
def dummyfy(request, monkeypatch):
    '''Patch lowlevel loader functions to rerturn dummy results.'''
    def fake_loader(path):
        if request.param == 'none':
            windows = {}
        else:
            windows = {'ABC': 'Test'}
        return request.param, windows
    for func in ('_load_sp', '_load_pc', '_load_c', '_load_f'):
        monkeypatch.setattr(lowlevel, func, fake_loader)
    return request.param

def rstrings(max_size):
    while True:
        yield ''.join(random.sample(string.lowercase, random.randint(1, max_size)))


### Tests ###
class TestKernelProperties(object):
    def test_kp_good(self, kernelfile):
        kprops = lowlevel.kernel_properties(kernelfile)
        assert kprops.path == kernelfile
        assert kprops.arch in lowlevel.ARCH
        assert kprops.type in lowlevel.KTYPE

    def test_kp_bad(self, nonkernelfile):
        with pytest.raises((ValueError, sm.SpiceError)):
            kprops = lowlevel.kernel_properties(nonkernelfile)

@pytest.mark.parametrize('ktype', list(lowlevel.KTYPE) + list(
    set(itt.islice(rstrings(10), 5)) - lowlevel.KTYPE
))
def test_info_type(ktype):
    info = lowlevel._info_type(ktype)
    if ktype in lowlevel.KTYPE:
        assert info in ('pos', 'rot', 'none')
    else:
        assert info == None

xValueError = pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize('arch', list(lowlevel.ARCH) + [xValueError('?')])
@pytest.mark.parametrize('ktype', list(lowlevel.KTYPE) + [
    xValueError(next(rstrings(10)))
])
def test_validate(arch, ktype):
    lowlevel._validate('Test', arch, ktype)

@pytest.mark.parametrize('recursive', [True, False])
def test_icollect_kprops(datadir, kernelfiles, recursive):
    paths = set(kp.path for kp in lowlevel.icollect_kprops(datadir, recursive, False))
    if not recursive:
        assert len(paths) < len(kernelfiles)
    assert paths - set(kernelfiles) == set()

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

#@pytest.mark.parametrize('filename', generate_filenames())
#def test_filter_extensions(filename):
#    assert lowlevel.filter_extensions(filename) in lowlevel.VALID_KERNEL_TYPES

@pytest.mark.usefixtures('dummyfy')
def test_load_any(kernelfile):
    if kernelfile.path.endswith('.bc'):
        pytest.xfail(reason='.bc files require a loaded sc kernel')
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
    return _abstract_loader_fixture(request, kernelfile, ['c'])

@pytest.mark.usefixtures('with_leapseconds', 'with_spacecraftclock')
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

# f
@pytest.fixture
def f_file(request, kernelfile):
    return _abstract_loader_fixture(request, kernelfile, ['f'])

@pytest.mark.usefixtures('with_leapseconds')
def test_load_f(f_file):
    info_type, time_window_map = lowlevel._load_f(f_file)
    assert info_type == 'pos'
    assert time_window_map != {}
