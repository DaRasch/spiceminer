#!/usr/bin/env python
#-*- coding:utf-8 -*-

from spiceminer.bodies import Body

import nose.tools as tools

@tools.raises(TypeError)
def test_init_fail_type():
    Body('MARS')

def test_cache():
    tools.assert_is(Body(0), Body(0))

