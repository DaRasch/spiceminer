#-*- coding:utf-8 -*-

import pytest

import random
import string
import itertools as itt
import collections

import spiceminer as sm
import spiceminer.kernel.lowlevel as lowlevel


### Helpers ###
def rstrings(max_size):
    while True:
        yield ''.join(random.sample(string.lowercase, random.randint(1, max_size)))

class FakeKernel(object):
    def __init__(self, path):
        self.path = path
        self.loaded = True

    def _unload(self):
        self.loaded = False

@pytest.fixture(scope='function')
def fake_LOADED(kernelfiles, monkeypatch):
    available = random.sample(kernelfiles, random.randint(0, len(kernelfiles)))
    substitute = {FakeKernel(path) for path in available}
    monkeypatch.setattr(lowlevel, 'LOADED_KERNELS', substitute)
    return substitute

@pytest.fixture(scope='function')
def fake_loaders(monkeypatch):
    '''Patch lowlevel loader functions to rerturn dummy results.'''
    def fake_loader(path):
        windows = {'ABC': 'Test'}
        return windows
    for func in ('_load_sp', '_load_pc', '_load_c', '_load_f'):
        monkeypatch.setattr(lowlevel, func, fake_loader)

@pytest.fixture(scope='function')
def fake_furnsh(monkeypatch):
    monkeypatch.setattr(lowlevel.spice, 'furnsh', lambda x: None)
    monkeypatch.setattr(lowlevel.spice, 'unload', lambda x: None)


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

def test_ifilter_kprops(kernelfiles, fake_LOADED):
    kp = collections.namedtuple('KernelPath', 'path')
    result = lowlevel.ifilter_kprops(kp(path) for path in kernelfiles)
    result_paths = set(kprops.path for kprops in result)
    fake_paths = set(k.path for k in fake_LOADED)
    assert result_paths.symmetric_difference(fake_paths) == set(kernelfiles)

def test_iunload_kprops(kernelfiles, fake_LOADED):
    kp = collections.namedtuple('KernelPath', 'path')
    result = lowlevel.iunload_kprops(kp(path) for path in kernelfiles)
    result_paths = set(kprops.path for kprops in result)
    assert result_paths == set(kernelfiles)
    unloaded_paths = {k.path for k in fake_LOADED if not k.loaded}
    assert len(unloaded_paths) == len(fake_LOADED)

@pytest.mark.parametrize('types', [
    [random.choice(list(lowlevel.KTYPE)) for i in range(10)]
])
def test_split_kprops(types):
    kt = collections.namedtuple('KernelType', 'type')
    kpmisc, kpbody = lowlevel.split_kprops(kt(t) for t in types)
    body_types = {kt.type for kt in kpbody}
    misc_types = {kt.type for kt in kpmisc}
    assert body_types.union(lowlevel.KTYPE_BODY) == lowlevel.KTYPE_BODY
    assert misc_types.intersection(lowlevel.KTYPE_BODY) == set()
    assert body_types.union(misc_types) == set(types)




@pytest.mark.usefixtures('fake_loaders', 'fake_furnsh')
def test_load_any(kernelfile):
    kp = collections.namedtuple('KernelProperties', ['path', 'type'])
    kprops = kp(kernelfile, random.choice(list(lowlevel.KTYPE)))
    time_window_map = lowlevel.load_any(kprops)
    if kprops.type in lowlevel.KTYPE_BODY:
        assert time_window_map == {'ABC': 'Test'}
    else:
        assert time_window_map == {}

def test_unload_any():
    pass


@pytest.mark.parametrize('path', ['.'])
def test_load_dummy(path):
    assert lowlevel._load_dummy(path) == {}

@pytest.mark.usefixtures('with_leapseconds')
def test_load_sp(spfile):
    time_window_map = lowlevel._load_sp(spfile)
    assert time_window_map != {}

@pytest.mark.usefixtures('with_leapseconds', 'with_spacecraftclock')
def test_load_c(cfile):
    time_window_map = lowlevel._load_c(cfile)
    assert time_window_map != {}

@pytest.mark.usefixtures('with_leapseconds')
def test_load_pc(pcfile):
    time_window_map = lowlevel._load_pc(pcfile)
    assert time_window_map != {}

@pytest.mark.usefixtures('with_leapseconds')
def test_load_f(ffile):
    time_window_map = lowlevel._load_f(ffile)
    assert time_window_map != {}
