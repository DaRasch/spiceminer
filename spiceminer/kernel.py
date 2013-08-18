#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

import spiceminer._spicewrapper as spice
import spiceminer.bodies as bodies

from spiceminer._helpers import ignored

__all__ = ['load', 'unload', 'get', 'LOADED_KERNELS']


LOADED_KERNELS = set()


def load(path='.'):
    def _loader(path):
        with ignored(spice.SpiceError):
            spice.furnsh(path)
            LOADED_KERNELS.add(path)
            return 1
        return 0
    return sum(sum(_loader(os.path.join(item[0], f)) for f in item[2])
        for item in os.walk(path))

def unload(path):
    def _unloader(path):
        LOADED_KERNELS.remove(path)
        spice.unload(path)
        return 1
    try:
        _unloader(path)
    except KeyError:
        return sum(_unloader(item) for item in tuple(LOADED_KERNELS) if path in item)

def get(body_id):
    if isinstance(body_id, basestring):
        body_id = spice.bodn2c(body_id)
        if body_id is not None:
            return bodies.Body(body_id)
        raise ValueError('get() got invalid name {}'.format(body_id))
    elif isinstance(body_id, int):
        if spice.bodc2n(body_id) is not None:
            return bodies.Body(body_id)
        raise ValueError('get() got invalid ID {}'.format(body_id))
    msg = 'get() integer or str argument expected, got {}'
    raise TypeError(msg.format(type(body_id)))
