#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy

from ctypes import *

cspice = CDLL('libspice.so')

class SpiceError(Exception):
    pass

def ckgp(spacecraft_id, instrument_id, et, tol, ref_frame):
    cmat = c_int * 9
    clkout = c_double()
    found = c_int()
    error_msg = cspice.ckgp_custom(spacecraft_id, instrument_id, et, tol,
        ref_frame, cmat, byref(clkout), byref(found))
    if error_msg:
        raise SpiceError(error)
    if not found:
        raise Exception('No data found') #TODO find good exception
    return (numpy.array(cmat).reshape(3, 3), float(clkout))
