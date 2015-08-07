#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re

from .. import _spicewrapper as spice
from ..time_ import Time
from .._helpers import ignored, TimeWindow


VALID_BODY_KERNEL_EXT = ('sp', 'c', 'sc', 'pc', 'f')
VALID_MISC_KERNEL_EXT = ('ls',)
VALID_KERNEL_EXT = VALID_BODY_KERNEL_EXT + VALID_MISC_KERNEL_EXT

def filter_extensions(filename):
    '''Check for correct extension and return kernel type.'''
    extension = (filename.rsplit('.', 1)[1:] or [''])[0]
    match = re.match('(b|t)(s?c|sp|f|ls|pc)$', extension)
    if not match:
        msg = 'Invalid file extension, got {}'
        raise ValueError(msg.format(extension))
    return match.string[1:]

def load_any(path, extension):
    '''Load **any** file and associated windows if necessary.'''
    loaders = {
        'sp': _load_sp,
        'c': _load_c,
        'pc': _load_pc,
        'f': _load_f
    }
    objects = ('misc', {})
    with ignored(KeyError):
        objects = loaders[extension](path)
    spice.furnsh(path)
    return objects


# Abstract loading mechanisms
_IDS = spice.SpiceCell.integer(1000)
_WINDOWS = spice.SpiceCell.double(100)

def _loader_template_bin(getter_ids, getter_times, path):
    getter_ids(path, _IDS)
    result = {}
    for idcode in _IDS:
        _WINDOWS.reset()
        getter_times(path, idcode, _WINDOWS)
        # Create new time windows
        windows = ((Time.fromet(et0), Time.fromet(et1))
            for et0, et1 in zip(_WINDOWS[::2], _WINDOWS[1::2]))
        result[idcode] = TimeWindow(*windows)
    return result

def _loader_template_txt(regex, path):
    with open(path, 'r') as f:
        idcodes = map(int, re.findall(regex, f.read()))
        return {idcode: TimeWindow() for idcode in idcodes}


# Condrete loaders for specific file formats
def _load_sp(path):
    '''Load sp kernel and associated windows.'''
    _IDS.reset()
    kernel_type = 'pos'
    try:
        result = _loader_template_bin(spice.spkobj, spice.spkcov, path)
    except spice.SpiceError:
        # Parse text kernels seperately
        result = _loader_template_txt('BODY([-0-9]*)_PM', path)
    return kernel_type, result

def _load_c(path):
    '''Load c kernel and associated windows.'''
    _IDS.reset()
    kernel_type = 'rot'
    result = _loader_template_bin(spice.ckobj, spice.ckcov, path)
    return kernel_type, result

def _load_pc(path):
    '''Load pc kernel and associated windows.'''
    _IDS.reset()
    kernel_type = 'rot'
    try:
        result = _loader_template_bin(spice.pckfrm, spice.ckcov, path)
    except spice.SpiceError:
        # Parse text kernels seperately
        result = _loader_template_txt('BODY([-0-9]*)_PM', path)
    return kernel_type, result

def _load_f(path):
    '''Load f kernel.'''
    return _loader_template_txt('FRAME([-0-9]*)_NAME', path)
