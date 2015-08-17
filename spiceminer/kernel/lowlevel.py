#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import re

from .. import _spicewrapper as spice
from ..time_ import Time
from .._helpers import ignored, TimeWindows

#: All possible type identifiers for kernels containing body transformation info.
VALID_BODY_KERNEL_TYPES = ('sp', 'c', 'sc', 'pc', 'f')
#: All possible type identifiers for kernels not containing body transformation info.
VALID_MISC_KERNEL_TYPES = ('ls',)
#: All possible kernel type identifiers.
VALID_KERNEL_TYPES = VALID_BODY_KERNEL_TYPES + VALID_MISC_KERNEL_TYPES

def filter_extensions(filename):
    '''Check for correct extension and return kernel type.

    Parameters
    ----------
    filename: str
        A file name of the format `name.extension` or `.extension`. Providing
        only `extension` will raise an error, even if the extension is valid.

    Returns
    -------
    str
        The kernel type identifier part of the extension (basically
        `extension[1:]`).

    Raises
    ------
    ValueError
        If the extension is invalid (does not match `(b|t)(s?c|sp|f|ls|pc)$`).
    '''
    extension = (filename.rsplit('.', 1)[1:] or [''])[0]
    match = re.match('^(b|t)(s?c|sp|f|ls|pc)$', extension)
    if not match:
        msg = 'Invalid file extension, got {}'
        raise ValueError(msg.format(filename))
    return match.string[1:]

def load_any(path, kernel_type):
    '''Load any valid kernel file and associated windows if necessary.

    Parameters
    ----------
    path: str
        A path to an existing file.
    kernel_type: str
        A kernel type identifier defined in `VALID_KERNEL_TYPES`

    Returns
    -------
    info_type: {'pos', 'rot', 'none'}
        What kind of transformation information is provided by the kernel.
    window_map: dict[int: list[tuple[Time, Time]]]
        List of time windows for which the transformation information is
        provided, mapped to the respective body id.
    '''
    if not os.path.isfile(path):
        raise IOError(2, 'No such file', path)
    if kernel_type not in VALID_KERNEL_TYPES:
        msg = 'Invalid kernel type, expected one of {}, got {}'
        raise ValueError(msg.format(VALID_KERNEL_TYPES, kernel_type))
    loader = {
        'sp': _load_sp,
        'c': _load_c,
        'sc': _load_c,
        'pc': _load_pc,
        'f': _load_f
    }.get(kernel_type, _load_dummy)
    info_type, window_map = loader(path)
    spice.furnsh(path)
    return info_type, window_map

def unload_any(kernel):
    spice.unload(kernel.path)


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
        result[idcode] = TimeWindows(*windows)
    return result

def _loader_template_txt(regex, path):
    with open(path, 'r') as f:
        return {int(i): TimeWindows() for i in re.findall(regex, f.read())}


# Concrete loaders for specific file formats
def _load_dummy(path):
    '''Dummy loader for kernels not covered by any other loader.'''
    return 'none', {}

def _load_sp(path):
    '''Load sp kernel and associated windows.'''
    _IDS.reset()
    try:
        result = _loader_template_bin(spice.spkobj, spice.spkcov, path)
    except spice.SpiceError as e:
        if 'needed to compute Delta ET' in e.message:
            #TODO: find better way to distinguish errors
            raise spice.SpiceError('No leap second kernel loaded')
        # Parse text kernels seperately
        with ignored(IOError):
            result = _loader_template_txt('BODY([-0-9]*)_PM', path)
        if result == {}:
            raise e
    return 'pos', result

def _load_c(path):
    '''Load c kernel and associated windows.'''
    _IDS.reset()
    result = _loader_template_bin(spice.ckobj, spice.ckcov, path)
    return 'rot', result

def _load_pc(path):
    '''Load pc kernel and associated windows.'''
    _IDS.reset()
    try:
        result = _loader_template_bin(spice.pckfrm, spice.ckcov, path)
    except spice.SpiceError as e:
        if 'needed to compute Delta ET' in e.message:
            #TODO: find better way to distinguish errors
            raise spice.SpiceError('No leap second kernel loaded')
        # Parse text kernels seperately
        with ignored(IOError):
            result = _loader_template_txt('BODY([-0-9]*)_PM', path)
        if result == {}:
            raise e
    return 'rot', result

def _load_f(path):
    '''Load f kernel.'''
    result = _loader_template_txt('FRAME([-0-9]*)_NAME', path)
    if not result:
        msg = 'Not a valid frame kernel: {}'
        raise spice.SpiceError(msg.format(path))
    return 'pos', result
