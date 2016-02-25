#-*- coding:utf-8 -*-

import pytest

import collections

import numpy as np

import spiceminer as sm
import spiceminer.bodies as bodies
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

@pytest.fixture(scope='function')
def make_bodies():
    '''Run with bodies made.'''
    ids = [10, 301, 399, 499]
    for item in ids:
        bodies.Body._make(item)

@pytest.yield_fixture(scope='function')
def clear_bodies():
    yield
    for id_, count in bodies._BodyMeta._ID_COUNTER.items():
        for i in range(count):
            if id_ != 0:
                bodies.Body._delete(id_)

### Data ###
VALID_PARAMETERS = [
    0,
    10,
    399,
    399.6,
    '399',
    '399.5',
    'EARTH',
    'earth',
    'Earth',
    ' EARTH',
    'EARTH ',
    'SOLAR SYSTEM BARYCENTER'
]

INVALID_PARAMETERS = [
    XFailType(1j),
    XFailValue('SOLARSYSTEMBARYCENTER'),
    XFailValue('EA RTH')
]

IDS = [10, 301, 399]

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
# TODO: _iterbodies, _typecheck

@pytest.mark.usefixtures('clear_bodies')
def test_make():
    assert len(bodies.Body.LOADED) == 1
    assert len(bodies.Barycenter.LOADED) == 1
    bodies.Body._make(399)
    assert len(bodies.Body.LOADED) == 2
    assert len(bodies.Planet.LOADED) == 1
    bodies.Body._make(399)
    assert len(bodies.Body.LOADED) == 2
    assert len(bodies.Planet.LOADED) == 1
    bodies.Body._make(10)
    assert len(bodies.Body.LOADED) == 3
    assert len(bodies.Planet.LOADED) == 1
    assert len(bodies.Star.LOADED) == 1
    assert all(type(x) == bodies.Planet for x in bodies.Planet.LOADED)

@pytest.mark.usefixtures('clear_bodies')
def test_delete():
    for i in [399, 399, 10]:
        bodies.Body._make(i)
    bodies.Body._delete(399)
    assert len(bodies.Body.LOADED) == 3
    assert len(bodies.Planet.LOADED) == 1
    bodies.Body._delete(399)
    assert len(bodies.Body.LOADED) == 2
    assert bodies.Planet.LOADED == set()
    bodies.Body._delete(10)
    assert len(bodies.Body.LOADED) == 1
    assert bodies.Star.LOADED == set()
    with pytest.raises(ValueError):
        bodies.Body._delete(10)

@pytest.mark.usefixtures('make_bodies', 'clear_bodies')
@pytest.mark.parametrize('arg', VALID_PARAMETERS + INVALID_PARAMETERS)
def test_constructor(arg):
    body = bodies.Body(arg)
    assert body is bodies.Body(arg)


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

    @pytest.mark.parametrize('idcode', IDS)
    @pytest.mark.parametrize('times', TIMES)
    def test_state(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.state(times)
        assert data.shape == (8, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode', IDS)
    @pytest.mark.parametrize('times', TIMES)
    def test_position(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.position(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode', IDS)
    @pytest.mark.parametrize('times', TIMES)
    def test_speed(self, idcode, times):
        cols = self._cols(times)
        body = sm.Body(idcode)
        data = body.speed(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    @pytest.mark.parametrize('idcode', IDS)
    @pytest.mark.parametrize('times', TIMES)
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
