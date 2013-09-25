#-*- coding:utf-8 -*-

import pytest


from spiceminer.bodies import Body


### Fixtures ###
@pytest.fixture(scope='function')
def reset_cache():
    Body._CACHE = {}


### No kernels needed ###
def test_constructor():
    body = Body(399)
    assert body.id == 399
    assert body.name == 'EARTH'
    pytest.raises(ValueError, Body, 398)
    pytest.raises(TypeError, Body, 399.5)
    with pytest.raises(AttributeError):
        body.id = 10
    with pytest.raises(AttributeError):
        body.name = 'MARS'

def test_cache(reset_cache):
    assert Body._CACHE == {}
    assert Body(301) is Body(301)

def test_children():
    assert Body(399).children() == [Body(301)]

def test_parent():
    assert Body(301).parent() == Body(399)


### Kernels needed ###
def test_state(kernels):
    assert Body(399).state(0) is not None

def test_position():
    assert Body(399).position(0) is not None

def test_speed():
    assert Body(399).speed(0) is not None
