#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import glob
import ctypes

import numpy

from ctypes import c_void_p, c_int, c_double, c_char_p, cast, sizeof, byref, POINTER, Structure

cwrapper = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libspice.*')
cwrapper = next(glob.iglob(cwrapper)) #TODO find better system independant alternative for glob
cspice = ctypes.CDLL(cwrapper)
cspice.erract_custom('SET', 'RETURN')
cspice.errdev_custom('SET', 'NULL')
del cwrapper
del os, glob


### Exceptions ###
class SpiceError(Exception):
    '''Special exception only raised by the low level c-API.'''
    pass


### helper classes/functions ###
class SpiceCell(Structure):
    DATATYPES_ENUM = {'char': 0, 'double': 1, 'int': 2, 'time': 3, 'bool': 4}
    DATATYPES_CLS = [c_char_p, c_double, c_int, c_int, c_int]
    CTRLBLOCK = 6

    _fields_ = [('dtype', c_int),
                ('length', c_int),
                ('size', c_int),
                ('card', c_int),
                ('isSet', c_int),
                ('adjust', c_int),
                ('init', c_int),
                ('base', c_void_p),
                ('data', c_void_p)]

    def __init__(self, dtype, length, size, card, isSet, init, base, data):
        self.dtype = dtype
        self.length = length
        self.size = size
        self.card = card
        self.isSet = isSet
        self.adjust = 0 # Always False, because not implemented
        self.init = init
        self.base = base
        self.data = data

    @classmethod
    def integer(cls, size):
        base = (c_int * (cls.CTRLBLOCK + size))()
        data = (c_int * size).from_buffer(base, cls.CTRLBLOCK * 4)
        instance = cls(cls.DATATYPES_ENUM['int'], 0, size, 0, 1, 0,
                       cast(base, c_void_p),
                       cast(data, c_void_p))
        return instance

    @classmethod
    def double(cls, size):
        base = (c_double * (cls.CTRLBLOCK + size))()
        data = (c_double * size).from_buffer(base, cls.CTRLBLOCK * 8)
        instance = cls(cls.DATATYPES_ENUM['double'], 0, size, 0, 1, 0,
                       cast(base, c_void_p),
                       cast(data, c_void_p))
        return instance

    def __len__(self):
        return self.card

    def __iter__(self):
        bytesize = sizeof(self.DATATYPES_CLS[self.dtype])
        resfunc = self.DATATYPES_CLS[self.dtype].from_address
        card, data = self.card or 1, self.data
        for i in xrange(card):
            yield resfunc(data + (i % card) * bytesize).value

    def __contains__(self, key):
        return key in self.__iter__()

    def __getitem__(self, key):
        bytesize = sizeof(self.DATATYPES_CLS[self.dtype])
        resfunc = self.DATATYPES_CLS[self.dtype].from_address
        card, data = self.card, self.data
        if isinstance(key, slice):
            start, stop, step = key.start or 0, key.stop or -1, key.step or 1
            #TODO Typechecking
            if card == 0:
                return []
            else:
                return list(resfunc(data + i * bytesize).value
                    for i in xrange(start % card, stop % card + 1, step))
        if key in xrange(-card, card):
            return resfunc(data + (key % card) * bytesize).value
        elif not isinstance(key, int):
            'SpiceCell inices must be integers, not {}'.format(type(key))
            raise TypeError(msg)
        else:
            raise IndexError('SpiceCell index out of range')


def errcheck(result, func, args):
    if result:
        raise SpiceError(result)
    return args[-1] #XXX is -1 always 'found'?


### Kernel/Frame id <-> name ###
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

cspice.namfrm_custom.argtypes = [c_char_p, POINTER(c_int)]
cspice.namfrm_custom.restype = c_char_p
cspice.namfrm_custom.errcheck = errcheck
def namfrm(name):
    code = c_int()
    cspice.namfrm_custom(name, byref(code))
    if code == 0:
        return None
    return code.value

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

cspice.spkobj_custom.argtypes = [c_char_p, POINTER(SpiceCell)]
cspice.spkobj_custom.restype = c_char_p
cspice.spkobj_custom.errcheck = errcheck
def spkobj(path, cell):
    cspice.spkobj_custom(path, byref(cell))

### Time conversion ###
cspice.utc2et_custom.argtypes = [c_char_p, POINTER(c_double)]
cspice.utc2et_custom.restype = c_char_p
cspice.utc2et_custom.errcheck = errcheck
def utc2et(time_string): # Outdatet and unused
    et = c_double()
    cspice.utc2et_custom(time_string, byref(et))
    return et.value

cspice.deltet_custom.argtypes = [c_double, c_char_p, POINTER(c_double)]
cspice.deltet_custom.restype = c_char_p
cspice.deltet_custom.errcheck = errcheck
def deltet(time, source_format):
    delta = c_double()
    cspice.deltet_custom(time, source_format, byref(delta))
    return delta.value

cspice.unitim_custom.argtypes = [POINTER(c_double), c_char_p, c_char_p]
cspice.unitim_custom.restype = c_char_p
cspice.unitim_custom.errcheck = errcheck
def unitim(et, insys, outsys):
    et = c_double(et)
    cspice.unitim_custom(byref(et), insys, outsys)
    return et.value

### Get position, velocity, etc. ###
cspice.spkpos_custom.argtypes = [c_char_p, c_double, c_char_p, c_char_p,
    c_char_p, POINTER(c_double * 3), POINTER(c_double)]
cspice.spkpos_custom.restype = c_char_p
cspice.spkpos_custom.errcheck = errcheck
def spkpos(target, et, ref, abcorr, observer):
    output = (c_double * 3)()
    light_time = c_double()
    cspice.spkpos_custom(target, et, ref, abcorr, observer, byref(output),
        byref(light_time))
    return output[::], light_time.value #XXX is light_time usefull?

cspice.spkezr_custom.argtypes = [c_char_p, c_double, c_char_p, c_char_p,
    c_char_p, POINTER(c_double * 6), POINTER(c_double)]
cspice.spkezr_custom.restype = c_char_p
cspice.spkezr_custom.errcheck = errcheck
def spkezr(target, et, ref, abcorr, observer):
    output = (c_double * 6)()
    light_time = c_double()
    cspice.spkezr_custom(target, et, ref, abcorr, observer, byref(output),
        byref(light_time))
    return output[::], light_time.value #XXX is light_time usefull?

cspice.pxform_custom.argtypes = [c_char_p, c_char_p, c_double,
    POINTER(c_double * 9)]
cspice.pxform_custom.restype = c_char_p
cspice.pxform_custom.errcheck = errcheck
def pxform(from_, to, et):
    output = (c_double * 9)()
    cspice.pxform_custom(from_, to, et, byref(output))
    return output[:]

cspice.ckgp_custom.argtypes = [c_int, c_int, c_double, c_double, c_char_p,
    POINTER(c_double * 9), POINTER(c_double), POINTER(c_int)]
cspice.ckgp_custom.restype = c_char_p
cspice.ckgp_custom.errcheck = errcheck
def ckgp(spacecraft_id, instrument_id, et, tol, ref_frame):
    cmat = (c_double * 9)()
    clkout = c_double()
    found = c_int()
    cspice.ckgp_custom(spacecraft_id, instrument_id, et, tol, ref_frame,
        byref(cmat), byref(clkout), byref(found))
    if not found:
        return None
    return (numpy.array(cmat).reshape(3, 3), float(clkout))
