#!/usr/bin/env python
#-*- coding:utf-8 -*-

from shared import load_base
load_base()

from spiceminer.bodies import Body

import nose.tools as tools

def test_constructor_valid():
    x = Body(499)
    tools.assert_equal(x.id, 499)
    tools.assert_equal(x.name, 'MARS')

def test_cache():
    tools.assert_is(Body(499), Body(499))

def test_meth_parent_valid():
    x = Body(499)
    tools.assert_is(x.parent(), Body(10))

def test_meth_children_valid():
    x = Body(499)
    tools.assert_equal(x.children(), [Body(401), Body(402)])

def test_meth_state_valid():
    Body(499).state(0)

def test_meth_position_valid():
    Body(499).position(0)

def test_meth_speed_valid():
    Body(499).speed(0)

@tools.raises(TypeError)
def test_constructor_fail_type():
    Body('499')
    Body('MARS')

@tools.raises(ValueError)
def test_construcotr_fail_value():
    Body(403)
