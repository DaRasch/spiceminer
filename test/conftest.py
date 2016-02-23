#-*- coding:utf-8 -*-

import pytest

import os
import random
import collections

import spiceminer._spicewrapper as spice
import spiceminer.kernel as kernel


MAX_FILES = 10

PKG_ROOT = os.path.realpath(os.path.join(__file__, '..', '..'))

DATA_ROOT = os.getenv('SPICEMINERDATA', os.path.join(PKG_ROOT, 'data'))
if not os.path.isdir(DATA_ROOT):
    DATA_ROOT = None

def _iter_files(root):
    if not root:
        raise StopIteration()
    for dirname, _, filenames in os.walk(root):
        for fname in filenames:
            yield os.path.join(dirname, fname)

DATA_FILES = list(_iter_files(DATA_ROOT))
random.shuffle(DATA_FILES)

def _filter_kernels(paths):
    types = collections.defaultdict(list)
    files = []
    for path in paths:
        try:
            arch, ktype = spice.getfat(path)
        except spice.SpiceError:
            continue
        if arch != '?' and ktype != '?':
            types[ktype.lower()].append(path)
            files.append(path)
    return types, files

TYPED_FILES, KERNEL_FILES = _filter_kernels(DATA_FILES)
NONKERNEL_FILES = list(set(DATA_FILES) - set(KERNEL_FILES))

def pytest_namespace():
    return {}


### Argument fixtures ###
@pytest.fixture(scope='session')
def datadir():
    if DATA_ROOT is None:
        pytest.skip('No data directory available.')
    return DATA_ROOT

@pytest.fixture(scope='session', params=DATA_FILES[:MAX_FILES])
@pytest.mark.skipif(not DATA_FILES,
    reason='No data in data directory. [{}]'.format(DATA_ROOT))
def datafile(request):
    return request.param

@pytest.fixture(scope='session')
@pytest.mark.skipif(not KERNEL_FILES,
    reason='No kernels in data directory. [{}]'.format(DATA_ROOT))
def kernelfiles(datadir):
    return KERNEL_FILES

@pytest.fixture(scope='session', params=KERNEL_FILES[:MAX_FILES])
@pytest.mark.skipif(not KERNEL_FILES,
    reason='No kernels in data directory. [{}]'.format(DATA_ROOT))
def kernelfile(request):
    return request.param

@pytest.fixture(scope='session', params=NONKERNEL_FILES[:MAX_FILES])
@pytest.mark.skipif(not NONKERNEL_FILES,
    reason='No non-kernels in data directory. [{}]'.format(DATA_ROOT))
def nonkernelfile(request):
    return request.param

@pytest.fixture(scope='session', params=TYPED_FILES['sp'][:MAX_FILES])
@pytest.mark.skipif(not TYPED_FILES['sp'],
    reason='No sp kernels in data directory. [{}]'.format(DATA_ROOT))
def spfile(request):
    return request.param

@pytest.fixture(scope='session', params=TYPED_FILES['c'][:MAX_FILES])
@pytest.mark.skipif(not TYPED_FILES['c'],
    reason='No c kernels in data directory. [{}]'.format(DATA_ROOT))
def cfile(request):
    return request.param

@pytest.fixture(scope='session', params=TYPED_FILES['pc'][:MAX_FILES])
@pytest.mark.skipif(not TYPED_FILES['pc'],
    reason='No pc kernels in data directory. [{}]'.format(DATA_ROOT))
def pcfile(request):
    return request.param

@pytest.fixture(scope='session', params=TYPED_FILES['f'][:MAX_FILES])
@pytest.mark.skipif(not TYPED_FILES['f'],
    reason='No f kernels in data directory. [{}]'.format(DATA_ROOT))
def ffile(request):
    return request.param


### Marker fixtures ###
@pytest.yield_fixture(scope='function')
def with_leapseconds(datadir):
    for path in KERNEL_FILES:
        if spice.getfat(path)[1] == 'ls':
            k = kernel.load(path).pop()
            break
    else:
        pytest.skip('No leap seconds kernel available.')
    yield
    k._unload()

@pytest.yield_fixture(scope='function')
def with_spacecraftclock(datadir):
    paths = [path for path in KERNEL_FILES if spice.getfat(path)[1] == 'sc']
    if not paths:
        pytest.skip('No spacecraft clock kernel available.')
    kernels = set.union(*(kernel.load(path) for path in paths))
    yield
    for k in kernels:
        k._unload()




@pytest.fixture(scope='function')
def load_kernels(datadir):
    kernel.load(datadir)

@pytest.yield_fixture(scope='function')
def unload_kernels(datadir):
    yield
    kernel.unload(datadir)
