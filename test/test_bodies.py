#-*- coding:utf-8 -*-

import pytest

import spiceminer
import spiceminer.bodies as bodies
from spiceminer.bodies import Body


### Fixtures ###
@pytest.fixture(scope='function')
def clear_cache():
    Body._CACHE = {}

@pytest.yield_fixture(scope='class')
def with_kernels(datadir):
    spiceminer.kernel.load(datadir)
    yield
    spiceminer.kernel.unload(datadir)


### No kernels needed ###
def gen_constructor():
    yield pytest.mark.xfail(raises=TypeError)([399.5, None, None, None, None])
    yield pytest.mark.xfail(raises=TypeError)(['EARTH', None, None, None, None])
    yield pytest.mark.xfail(raises=ValueError)([398, None, None, None, None])
    yield 399, 'EARTH', [301], 10, bodies.Planet
    yield 301, 'MOON', [], 399, bodies.Satellite
    yield 499, 'MARS', [401, 402], 10, bodies.Planet
    yield 10, 'SUN', [i for i in range(199, 1000, 100)], 0, bodies.Star
    yield 0, 'SOLAR SYSTEM BARYCENTER', [], None, bodies.Barycenter

@pytest.mark.usefixtures('clear_cache')
@pytest.mark.parametrize('idcode,name,children,parent,class_', gen_constructor())
def test_constructor(idcode, name, children, parent, class_):
    # constructor and cache
    assert idcode not in Body._CACHE
    body = Body(idcode)
    assert idcode in Body._CACHE
    assert body is Body._CACHE[idcode]
    assert Body(idcode) is body
    assert type(body) is class_
    # properties
    assert body.id == idcode
    assert body.name == name
    with pytest.raises(AttributeError):
        body.id = idcode
    with pytest.raises(AttributeError):
        body.name = name
    # parent/children
    try:
        assert body.parent().id == parent
    except AttributeError:
        assert type(body) is bodies.Barycenter
        assert body.parent() is None
    assert [child.id for child in body.children()] == children


def gen_get_nokernels():
    yield 10, 10
    yield 'SUN', 10
    yield 'sun', 10
    yield 'SuN', 10

@pytest.mark.parametrize('arg,expected', gen_get_nokernels())
def test_get_nokernels(arg, expected):
    with pytest.raises(ValueError):
        bodies.get(arg)


### Kernels needed ###
def gen_data():
    yield pytest.mark.xfail(raises=TypeError)([399, None])
    yield pytest.mark.xfail(raises=ValueError)([399, 'a'])
    yield pytest.mark.xfail(raises=ValueError)([399, 'asdf'])
    for idcode in (399, 301, 499, 401, 402, 10):
        yield idcode, 0
        yield idcode, spiceminer.Time()
        yield idcode, list(spiceminer.frange(spiceminer.Time(2000), spiceminer.Time(2000, 2), spiceminer.Time.DAY))

@pytest.mark.usefixtures('with_kernels')
@pytest.mark.parametrize('idcode,times', list(gen_data()))
class TestBodyData:
    def _cols(self, times):
        try:
            cols = len(times)
        except Exception:
            cols = 1
        return cols

    def test_state(self, idcode, times):
        cols = self._cols(times)
        body = Body(idcode)
        data = body.state(times)
        assert data.shape == (8, cols)
        assert data.dtype == float

    def test_position(self, idcode, times):
        cols = self._cols(times)
        body = Body(idcode)
        data = body.position(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    def test_speed(self, idcode, times):
        cols = self._cols(times)
        body = Body(idcode)
        data = body.speed(times)
        assert data.shape == (4, cols)
        assert data.dtype == float

    def test_rotation(self, idcode, times):
        cols = self._cols(times)
        body = Body(idcode)
        data = body.rotation(times)
        assert len(data) == 2
        assert len(data[0]) == cols
        assert data[0].dtype == float
        for matrix in data[1]:
            assert matrix.shape == (3, 3)
            assert matrix.dtype == float


def gen_get():
    yield pytest.mark.xfail(raises=TypeError)((10.5, None))
    yield pytest.mark.xfail(raises=ValueError)(('asdf', None))
    yield pytest.mark.xfail(raises=ValueError)((11, None))

@pytest.mark.usefixtures('with_kernels')
@pytest.mark.parametrize('arg,expected', list(gen_get()) + list(gen_get_nokernels()))
def test_get(arg, expected):
    assert bodies.get(arg) is Body(expected)
