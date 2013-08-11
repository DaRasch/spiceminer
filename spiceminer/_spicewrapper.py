#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ctypes import *

cspice = CDLL('libspice.so')


def ckgp(spacecraft_id, instrument_id, et, tol, ref_frame):
    cmat = c_int * 9
    clkout = c_double()
    found = c_int()
    cspice.ckgp_c2(spacecraft_id, instrument_id, et, tol, ref_frame, cmat,
        byref(clkout), byref(found))
    if not found:
        raise Exception()
    return
