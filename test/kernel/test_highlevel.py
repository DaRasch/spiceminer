#-*- coding:utf-8 -*-

import pytest

import os
import random
import collections

import spiceminer.kernel.highlevel as highlevel
import spiceminer._helpers as helpers
from spiceminer._helpers import cleanpath


### Fixtures ###
@pytest.fixture(scope='function', params=['pos', 'rot', 'none'])
def patch_lowlevel(request, monkeypatch):
    def fake_load_any(path, kernel_type):
        if request.param == 'none':
            windows = {}
        else:
            windows = {10: helpers.TimeWindows()}
        return request.param, windows
    def fake_unload_any(kernel):
        pass
    monkeypatch.setattr(highlevel, 'load_any', fake_load_any)
    monkeypatch.setattr(highlevel, 'unload_any', fake_unload_any)
    return request.param

@pytest.yield_fixture
def reset_Kernel():
    yield
    highlevel.Kernel.LOADED = set()
    highlevel.Kernel.TIMEWINDOWS_POS = collections.defaultdict(helpers.TimeWindows)
    highlevel.Kernel.TIMEWINDOWS_ROT = collections.defaultdict(helpers.TimeWindows)


### Kernel ###
@pytest.mark.usefixtures('reset_Kernel')
@pytest.mark.parametrize('path,kernel_type', [('/home/user', 'test'), ('/', 'test2')])
def test_cls_init(path, kernel_type, patch_lowlevel):
    k = highlevel.Kernel(path, kernel_type)
    # attributes
    assert isinstance(k.path, basestring)
    assert isinstance(k.name, basestring)
    assert k.type == kernel_type
    assert k.info == patch_lowlevel
    assert iter(k.ids)
    target = ''.join(['TIMEWINDOWS_', k.info.upper()])
    for i in k.ids:
        assert i in getattr(highlevel.Kernel, target, k.ids)
    assert k in highlevel.Kernel.LOADED
    # reload (no force_reload)
    with pytest.raises(ValueError):
        highlevel.Kernel(path, kernel_type, force_reload=False)
    # reload (force_reload)
    k2 = highlevel.Kernel(path, kernel_type, force_reload=True)
    assert k2 is k
    assert k2 in highlevel.Kernel.LOADED
    assert len(highlevel.Kernel.LOADED) == 1

@pytest.mark.usefixtures('reset_Kernel')
@pytest.mark.parametrize('path,kernel_type', [('/home/user', 'test'), ('/', 'test2')])
def test_cls_unload(path, kernel_type, patch_lowlevel):
    k = highlevel.Kernel(path, kernel_type)
    target = ''.join(['TIMEWINDOWS_', k.info.upper()])
    target = getattr(highlevel.Kernel, target, None)
    # loaded correctly? redundant because of test_cls_init but better safe than sorry
    assert k in highlevel.Kernel.LOADED
    if target is not None:
        for i in k.ids:
            assert i in target
    # unloaded correctly?
    k._unload()
    assert k not in highlevel.Kernel.LOADED
    if target is not None:
        for i in k.ids:
            assert i not in target


## Class methods ##
@pytest.mark.usefixtures('reset_Kernel')
@pytest.mark.parametrize('path,extension', [('/home/user.bsp', None), ('/', 'bsp')])
def test_load_single(path, extension, patch_lowlevel):
    kernel = highlevel.Kernel.load_single(path, extension)
    k = list(highlevel.Kernel.LOADED)[0]
    if extension is None:
        extension = path
    assert k.type == extension[-2:]
    assert k == kernel


# Need real kernels. TODO: Stop requiring live kernels?
@pytest.mark.usefixtures('unload_kernels')
def test_load(datadir):
    kernels = highlevel.Kernel.load(datadir)
    assert highlevel.Kernel.LOADED


# Need real kernels. TODO: Stop requiring live kernels?
@pytest.mark.usefixtures('load_kernels', 'unload_kernels')
def test_unload(datadir):
    kernels = highlevel.Kernel.unload(datadir)
    assert not highlevel.Kernel.LOADED
