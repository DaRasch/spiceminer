#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import glob
import ctypes
import functools
import numpy

from ctypes import c_int, c_double, c_char_p, byref, POINTER

cwrapper = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libspice.*')
cwrapper = next(glob.iglob(cwrapper)) #TODO find better system independant alternative for glob
cspice = ctypes.CDLL(cwrapper)
cspice.erract_custom('SET', 'RETURN')
del cwrapper
del os, glob


### Exceptions ###
class SpiceError(Exception):
    pass


### helper functions ###
def typecheck(f, *args): #XXX necessary? overhead vs. clear error message
    pass

def errcheck(result, func, args):
    if result:
        raise SpiceError(result)
    return args[-1] #XXX is -1 always 'found'?


### Kernel id <-> name ###
cspice.bodn2c_custom.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int)]
cspice.bodn2c_custom.restype = c_char_p
cspice.bodn2c_custom.errcheck = errcheck
def bodn2c(name):
    code = c_int()
    found = c_int()
    cspice.bodn2c_custom(name, byref(code), byref(found))
    if not found:
        return None
    return code.value

cspice.bodc2n_custom.argtypes = [c_int, c_char_p, POINTER(c_int)]
cspice.bodc2n_custom.restype = c_char_p
cspice.bodc2n_custom.errcheck = errcheck
def bodc2n(code):
    name = ctypes.create_string_buffer(256) #TODO move buffer creation to c-implementation
    found = c_int()
    cspice.bodc2n_custom(code, name, byref(found))
    if not found:
        return None
    return name.value

### Kernel (un)load ###
cspice.furnsh_custom.argtypes = [c_char_p]
cspice.furnsh_custom.restype = c_char_p
cspice.furnsh_custom.errcheck = errcheck
def furnsh(path):
    cspice.furnsh_custom(path)

cspice.unload_custom.argtypes = [c_char_p]
cspice.unload_custom.restype = c_char_p
cspice.unload_custom.errcheck = errcheck
def unload(path):
    cspice.unload_custom(path)

### Time conversion ###
cspice.utc2et_custom.argtypes = [c_char_p, POINTER(c_double)]
cspice.utc2et_custom.restype = c_char_p
cspice.utc2et_custom.errcheck = errcheck
def utc2et(time_string):
    et = c_double()
    cspice.utc2et_custom(time_string, byref(et))
    return et.value

cspice.unitim_custom.argtypes = [POINTER(c_double), c_char_p, c_char_p]
cspice.unitim_custom.restype = c_char_p
cspice.unitim_custom.errcheck = errcheck
def unitim(et, insys, outsys):
    et = c_double(et)
    cspice.unitim_custom(byref(et), insys, outsys)
    return et.value

### Get position, velocity, etc. ###
cspice.spkezr_custom.argtypes = [c_char_p, c_double, c_char_p, c_char_p,
    c_char_p, POINTER(c_double * 6), POINTER(c_double)]
cspice.spkezr_custom.restype = c_char_p
cspice.spkezr_custom.errcheck = errcheck
def spkezr(target, et, ref, abcorr, observer):
    output = (c_double * 6)()
    light_time = c_double()
    cspice.spkezr_custom(target, et, ref, abcorr, observer, byref(output),
        byref(light_time))
    return output[::], light_time.value

### get pointing ###
cspice.ckgp_custom.argtypes = [c_int, c_int, c_double, c_double, c_char_p,
    POINTER(c_double * 9), POINTER(c_double), POINTER(c_int)]
cspice.ckgp_custom.restype = c_char_p
cspice.ckgp_custom.errcheck = errcheck
def ckgp(spacecraft_id, instrument_id, et, tol, ref_frame):
    cmat = (c_int * 9)()
    clkout = c_double()
    found = c_int()
    cspice.ckgp_custom(spacecraft_id, instrument_id, et, tol, ref_frame,
        byref(cmat), byref(clkout), byref(found))
    if not found:
        return None
    return (numpy.array(cmat).reshape(3, 3), float(clkout))
