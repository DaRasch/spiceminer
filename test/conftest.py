#-*- coding:utf-8 -*-

import pytest

import os
import itertools as itt

import spiceminer.kernel as kernel


VALID_EXT = [''.join(ext) for ext in itt.product(('b', 't'), kernel.lowlevel.VALID_KERNEL_TYPES)]

PKG_ROOT = os.path.realpath(os.path.join(__file__, '..', '..'))
ROOT_DIR = PKG_ROOT

def get_files(root):
    for dir_path, _, files in os.walk(root):
        for name in files:
            kernel.lowlevel.filter_extensions(name)

DATA_DIR = os.getenv('SPICEMINERDATA', os.path.join(ROOT_DIR, 'data'))
if not os.path.isdir(DATA_DIR):
    DATA_DIR = None

def pytest_namespace():
    return {'datadir': DATA_DIR}

def check_datadir(func):
    if DATA_DIR is None:
        pytest.skip('No data dir available.')
    return func


### Fixtures ###
@pytest.fixture(scope='session')
def datadir():
    if DATA_DIR is None:
        pytest.skip('No data dir available.')
    return DATA_DIR

@pytest.yield_fixture(scope='function')
@check_datadir
def with_leapseconds():
    for dir_path, _ , fnames in os.walk(DATA_DIR):
        do_break = True
        for name in fnames:
            if name.endswith('ls'):
                path = os.path.join(dir_path, name)
                kernel.load(path)
                break
        else:
            do_break = False
        if do_break:
            break
    else:
        pytest.skip('No leap seconds kernel available')
    yield
    kernel.unload(path)


@pytest.fixture(scope='function')
@check_datadir
def load_kernels():
    kernel.load(DATA_DIR)

@pytest.yield_fixture(scope='function')
@check_datadir
def unload_kernels():
    yield
    kernel.unload(DATA_DIR)
