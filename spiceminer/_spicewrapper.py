#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import glob
import ctypes
import contextlib
import numpy

from ctypes import c_int, c_char, byref

cwrapper = os.path.join(os.path.dirname(__file__), 'libspice.*') #FIXME fails when module is loaded from within its own directory
cwrapper = next(glob.iglob(cwrapper))
print cwrapper or 'ERROR: No path to libspice' #TODO remove after testing
cspice = ctypes.CDLL(cwrapper)
del cwrapper

### Exceptions ###
class SpiceError(Exception):
    pass


### helper functions ###
@contextlib.contextmanager
def check_errors(): #TODO replace with ctypes capabilities
    error = yield
    if error:
        raise SpiceError(error)


### Kernel id <-> name ###
def bodn2c(name):
    code = c_int()
    found = c_int()
    with check_errors():
        cspice.bodn2c_custom(name, byref(code), byref(found))
    if not found:
        return None
    return int(code)

def bodc2n(code):
    name = c_char()
    found = c_int()
    with check_errors():
        cspice.bodc2n_custom(code, byref(name), byref(found))
    if not found:
        return None
    return int(code)


### get pointing ###
def ckgp(spacecraft_id, instrument_id, et, tol, ref_frame):
    cmat = c_int * 9
    clkout = c_double()
    found = c_int()
    error_msg = cspice.ckgp_custom(spacecraft_id, instrument_id, et, tol,
        ref_frame, cmat, byref(clkout), byref(found))
    if error_msg:
        raise SpiceError(error_msg)
    if not found:
        raise Exception('No data found') #TODO find good exception
    return (numpy.array(cmat).reshape(3, 3), float(clkout))
