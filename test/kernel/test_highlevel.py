#-*- coding:utf-8 -*-

import pytest

import os
import random
import collections

import spiceminer._helpers as helpers
import spiceminer.kernel.lowlevel as lowlevel
import spiceminer.kernel.highlevel as highlevel


### Helpers ###
@pytest.fixture(scope='function')
def patch_lowlevel(monkeypatch):
    def fake_load_any(kprops):
        if kprops.type in lowlevel.KTYPE_BODY:
            windows = {10: helpers.TimeWindows()}
        else:
            windows = {}
        return windows
    def fake_unload_any(kprops):
        pass
    monkeypatch.setattr(highlevel.lowlevel, 'load_any', fake_load_any)
    monkeypatch.setattr(highlevel.lowlevel, 'unload_any', fake_unload_any)

@pytest.yield_fixture(scope='function')
def clear_Kernel():
    yield
    highlevel.Kernel.LOADED.clear()
    highlevel.Kernel.TIMEWINDOWS_POS.clear()
    highlevel.Kernel.TIMEWINDOWS_ROT.clear()


### Tests ###
# Load
@pytest.mark.usefixtures('patch_lowlevel')
def test_load(datadir, kernelfiles):
    loaded = highlevel.Kernel.load(datadir)
    assert set(item.path for item in loaded) == set(kernelfiles)
    assert highlevel.Kernel.LOADED == loaded
    reloaded = highlevel.Kernel.load(datadir)
    assert reloaded == set()
    assert highlevel.Kernel.LOADED == loaded
    reloaded = highlevel.Kernel.load(datadir, force_reload=True)
    assert reloaded.intersection(loaded) == set()
    assert highlevel.Kernel.LOADED == reloaded

@pytest.mark.usefixtures('patch_lowlevel')
def test_load_errors(tempdir):
    with pytest.raises(IOError):
        loaded = highlevel.Kernel.load(tempdir)
    with pytest.raises(IOError):
        loaded = highlevel.Kernel.load(os.path.join(tempdir, 'test'))

# Unload
@pytest.mark.usefixtures('patch_lowlevel')
def test_unload(datadir):
    loaded = highlevel.Kernel.load(datadir)
    unloaded = highlevel.Kernel.unload(datadir)
    assert unloaded == loaded
    assert highlevel.Kernel.LOADED == set()

@pytest.mark.usefixtures('patch_lowlevel')
def test_unload_errors(tempdir):
    with pytest.raises(IOError):
        unloaded = highlevel.Kernel.unload(tempdir)
    with pytest.raises(IOError):
        unloaded = highlevel.Kernel.unload(os.path.join(tempdir, 'test'))

# class init/unload
@pytest.mark.usefixtures('patch_lowlevel', 'clear_Kernel')
def test_cls_init(kernelfile):
    kp = collections.namedtuple('KernelProperties', ['path', 'type'])
    kprops = kp(kernelfile, random.choice(list(lowlevel.KTYPE)))
    k = highlevel.Kernel(kprops)
    assert k.type == kprops.type
    assert k.path == kernelfile
    assert k in highlevel.Kernel.LOADED
    if k.type in lowlevel.KTYPE_BODY:
        assert list(k.bodies)[0].id == 10
        assert k.bodies == set.union(set(k.TIMEWINDOWS_POS.keys()), k.TIMEWINDOWS_ROT.keys())
    else:
        assert k.bodies == set()
        assert not k.TIMEWINDOWS_POS
        assert not k.TIMEWINDOWS_ROT

@pytest.mark.usefixtures('patch_lowlevel', 'clear_Kernel')
def test_cls_unload(kernelfile):
    kp = collections.namedtuple('KernelProperties', ['path', 'type'])
    kprops = kp(kernelfile, random.choice(list(lowlevel.KTYPE)))
    k = highlevel.Kernel(kprops)
    k._unload()
    assert k not in highlevel.Kernel.LOADED
    if k.type in lowlevel.KTYPE_BODY:
        print k.TIMEWINDOWS_POS
        print k.TIMEWINDOWS_ROT
        print k.type
        assert not k.TIMEWINDOWS_POS
        assert not k.TIMEWINDOWS_ROT
