#-*- coding:utf-8 -*-

import pytest

import os
import itertools as itt
from collections import namedtuple

import spiceminer.kernel as kernel


#VALID_EXT = [''.join(ext) for ext in itt.product(('b', 't'), kernel.lowlevel.VALID_KERNEL_TYPES)]

PKG_ROOT = os.path.realpath(os.path.join(__file__, '..', '..'))

DATA_DIR = os.getenv('SPICEMINERDATA', os.path.join(PKG_ROOT, 'data'))
if not os.path.isdir(DATA_DIR):
    DATA_DIR = None
print DATA_DIR

def _iter_files(root):
    if not root:
        raise StopIteration()
    kfile = namedtuple('KernelFile', ['path', 'type'])
    for dir_path, _, files in os.walk(root):
        for name in files:
            try:
                # FIXME remove dependency on internal spiceminer code
                kernel_type = kernel.lowlevel.filter_extensions(name)
                yield kfile(os.path.join(dir_path, name), kernel_type)
            except ValueError:
                pass

DATA_FILES = list(itt.islice(_iter_files(DATA_DIR), 10)) or [None]



def pytest_namespace():
    return {#'datadir': DATA_DIR,
    'needs_datafiles': pytest.mark.skipif(DATA_FILES == [None], reason='No data in data directory. [{}]'.format(DATA_DIR))}


### Fixtures ###
@pytest.fixture(scope='session')
def datadir():
    if DATA_DIR is None:
        pytest.skip('No data directory available.')
    return DATA_DIR

@pytest.fixture(scope='session')
def datafiles(datadir):
    if DATA_FILES == [None]:
        pytest.skip('No data in data directory. [{}]'.format(datadir))
    return DATA_FILES

@pytest.fixture(scope='session', params=DATA_FILES, ids=[f.path for f in DATA_FILES])
def kernelfile(request):
    if request.param is None:
        pytest.skip('No data in data directory. [{}]'.format(datadir))
    return request.param

@pytest.yield_fixture(scope='function')
def with_leapseconds(datafiles):
    for item in datafiles:
        if item.type == 'ls':
            kernel.load(item.path)
            break
    else:
        pytest.skip('No leap seconds kernel available')
    yield
    kernel.unload(item.path)


@pytest.fixture(scope='function')
def load_kernels(datadir):
    kernel.load(datadir)

@pytest.yield_fixture(scope='function')
def unload_kernels(datadir):
    yield
    kernel.unload(datadir)
