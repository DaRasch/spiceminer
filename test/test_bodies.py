#-*- coding:utf-8 -*-

import pytest

import collections

import numpy as np

import spiceminer as sm
import spiceminer._spicewrapper as spice


### Fixtures ###
XFailType = pytest.mark.xfail(raises=TypeError)
XFailValue = pytest.mark.xfail(raises=ValueError)

@pytest.yield_fixture(scope='class')
def with_kernels(datadir):
    '''Run tests with kernels loaded.'''
    sm.load(datadir)
    yield
    sm.unload(datadir)

class FakeKernel(object):
    def __init__(self):
        self.__class__.LOADED = {self}
        # All hardcoded body ids
        self.ids = {i for i in xrange(-100000, 200000) if spice.bodc2n(i)}
FakeKernel()

@pytest.fixture(scope='function')
def patch_kernel(monkeypatch):
    '''Fake Kernel to simulate all possible bodies beeing loaded.'''
    import spiceminer.bodies as bodies
    monkeypatch.setattr(bodies, 'Kernel', FakeKernel)


### Data generators ###
def gen_bodies():
    nt = collections.namedtuple('BodyAttributes',
        ['id', 'name', 'children', 'parent', 'class_'])
    yield nt(399, 'EARTH', [301], 10, sm.Planet)
    yield nt(301, 'MOON', [], 399, sm.Satellite)
    yield nt(499, 'MARS', [401, 402], 10, sm.Planet)
    yield nt(10, 'SUN', [i for i in range(199, 1000, 100)], 0, sm.Star)
    yield nt(0, 'SOLAR SYSTEM BARYCENTER', [], None, sm.Barycenter)

VALID_PARAMETERS = [399, '399', 'EARTH', 'earth', 'Earth', ' EARTH', 'EARTH ']
INVALID_PARAMETERS = [
    XFailType(1j),
    XFailType(399.5),
    XFailValue('399.5'),
    XFailValue('SOLARSYSTEMBARYCENTER'),
    XFailValue('EA RTH')
]

TIMES = [
    15.45,
    '15.45',
    sm.Time(),
    [0, 10],
    ['0', '10'],
    np.arange(sm.Time(2000), sm.Time(2000, 2), sm.Time.DAY, dtype=float),
    XFailType(None),
    XFailValue('a'),
    XFailValue('asdf'),
]

### No kernels needed ###
# TODO: _iterbodies, _typecheck, _BodyMeta

@pytest.mark.usefixtures('patch_kernel')
@pytest.mark.parametrize('arg', VALID_PARAMETERS + INVALID_PARAMETERS)
def test_constructor(arg):
    sm.Body(arg)

@pytest.mark.usefixtures('patch_kernel')
@pytest.mark.parametrize('arg,class_', [(x[0], x[-1]) for x in gen_bodies()])
def test_type(arg, class_):
    body = sm.Body(arg)
    assert isinstance(body, class_)
    assert isinstance(body, sm.Body)

@pytest.mark.usefixtures('patch_kernel')
@pytest.mark.parametrize('idcode,name,children,parent', [x[:4] for x in gen_bodies()])
def test_attributes(idcode, name, children, parent):
    body = sm.Body(idcode)
    assert body.id == idcode
    with pytest.raises(AttributeError):
        body.id = idcode
    assert body.name == name
    with pytest.raises(AttributeError):
        body.name = name
    assert body.children == [sm.Body(c) for c in children]
    if parent is not None:
        assert body.parent == sm.Body(parent)
    else:
        assert body.parent == None

@pytest.mark.usefixtures('patch_kernel')
@pytest.mark.parametrize('idcode,name', [x[:2] for x in gen_bodies()])
def test_equals(idcode, name):
    assert sm.Body(idcode) == sm.Body(name)


### Kernels needed ###
def gen_data():
    yield pytest.mark.xfail(raises=TypeError)([399, None])
    yield pytest.mark.xfail(raises=ValueError)([399, 'a'])
    yield pytest.mark.xfail(raises=ValueError)([399, 'asdf'])
    for idcode in (399, 301, 499, 401, 402, 10):
        yield idcode, 0
        yield idcode, sm.Time()
        yield idcode, np.arange(sm.Time(2000), sm.Time(2000, 2), sm.Time.DAY, dtype=float)

@pytest.mark.usefixtures('with_kernels')
class TestBodyData:
    def _cols(self, times):
        try:
            cols = len(times)
        except Exception:
            cols = 1
        if isinstance(times, basestring):
            cols = 1
        return cols

    @pytest.mark.parametrize('idcode', [x[0] for x in gen_bodies()])
    @pytest.mark.parametrize('times', TIMES)
    def test_state(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.state(times)
        assert data.shape == (8, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode,times', list(gen_data()))
    def test_position(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.position(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode,times', list(gen_data()))
    def test_speed(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.speed(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode,times', list(gen_data()))
    def test_rotation(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.rotation(times)
        assert len(data) == 2
        assert len(data[0]) == cols
        assert data[0].dtype == float
        for matrix in data[1]:
            assert matrix.shape == (3, 3)
            assert matrix.dtype == float
