#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

import spiceminer._spicewrapper as spice
import spiceminer.bodies as bodies

from spiceminer._helpers import ignored

__all__ = ['load', 'unload', 'get', 'LOADED_KERNELS']


LOADED_KERNELS = set()


# def load(path='.', recursions=99): #XXX use os.walk for recursion?
#     def _loader(path, recursions):
#         if os.path.isdir(path) and recursions > 0:
#             return sum(_loader(os.path.join(path, d), recursions - 1)
#                 for d in os.listdir(path))
#         with ignored(spice.SpiceError):
#             spice.furnsh(path)
#             LOADED_KERNELS.add(path)
#             return 1
#         return 0

#     count = _loader(path, recursions)
#     if count == 0:
#         raise IOError('no kernels loaded')
#     return count

def load(path='.'):
    def _loader(path):
        with ignored(spice.SpiceError):
            spice.furnsh(path)
            LOADED_KERNELS.add(path)
            return 1
        return 0
    return sum((_loader(os.path.join(item[0], f)) for f in item[2])
        for item in os.walk(path))


def unload(path):
    try:
        LOADED_KERNELS.remove(path)
        spice.unload(path)
    except KeyError:
        for item in LOADED_KERNELS:
            if path in item:
                LOADED_KERNELS.remove(item)
                spice.unload(item)

def get(body_id):
    if isinstance(body_id, basestring):
        body_id = spice.bodn2c(body_id)
        if body_id is not None:
            return bodies.Body(body_id)
        else:
            raise ValueError('get() got invalid name {}'.format(body_id))
    elif isinstance(body_id, int):
        if spice.bodc2n(body_id) is not None:
            return bodies.Body(body_id)
        else:
            raise ValueError('get() got invalid id {}'.format(body_id))
    else:
        msg = 'get() integer or str argument expected, got {}'
        raise TypeError(msg.format(type(body_id)))



