#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections

from .. import _spicewrapper as spice
from ..time_ import Time
from .._helpers import ignored, TimeWindows

### Constants ###
ARCH_BIN = {'DAF', 'DAS', 'NAIF'}
ARCH_TXT = {'KPL'}
ARCH = set.union(ARCH_BIN, ARCH_TXT)

KTYPE_POS = {'sp', 'f'}
KTYPE_ROT = {'c', 'pc'}
KTYPE_NONE = {'ls', 'sc'}
KTYPE_BODY = set.union(KTYPE_POS, KTYPE_ROT)
KTYPE = set.union(KTYPE_BODY, KTYPE_NONE)

### Shared vars ###
BODY_COUNTER = collections.Counter()
LOADED_BODIES = set()
LOADED_KERNELS = set()


### Kernel property parsing ###
kp = collections.namedtuple('KernelProperties', ['binary', 'arch', 'type', 'info'])
def kernel_properties(filepath):
    '''Collect kernel properties.

    Notes
    -----
    Identifier description:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#SPICE%20Kernel%20Type%20Identification
    Legal characters in text kernels:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#Text%20Kernel%20Specifications
    '''
    with open(filepath, 'rb') as file:
        identifier = file.read(8).decode('utf-8').strip()
    arch, ktype = _split_identifier(identifier)
    _validate(filepath, arch, ktype)
    binary = _is_binary(arch)
    info = _info_type(kernel_type)
    return kp(binary, arch, ktype, info)

def _split_identifier(identifier):
    try:
        i = identifier.index('/')
        arch = identifier[:i]
        ktype = identifier[i + 1:][:-1]
    except ValueError:
        arch = identifier[:3]
        ktype = identifier[3:6]
    return arch, ktype

def _is_binary(arch):
    return arch in ARCH_BIN

def _is_binary2(sample):
    for char in sample:
        if not ((32 <= ord(char) <= 126) or ord(cahr) == 9):
            return True
            break
    else:
        return False

def _info_type(ktype):
    if ktype in KTYPE_POS:
        return 'pos'
    elif ktype in KTYPE_ROT:
        return 'rot'
    elif ktype in KTYPE_NONE:
        return 'none'

def _validate(filepath, arch, ktype):
    if arch not in ARCH:
        raise ValueError('Not a kernel file: {}'.format(filepath))
    if ktype not in KTYPE:
        msg = "Unsupported kernel type '{}' in {}"
        raise ValueError(msg.format(ktype, filepath))


### Kernel loading ###
def load_any(filepath, kprops):
    loader = {
        'sp': _load_sp,
        'c': _load_c,
        'pc': _load_pc,
        'f': _load_f
    }.get(kprops.ktype, _load_dummy)
    loader(filepath)
    spice.furnsh(filepath)

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

def _validate_ls():
    if 'ls' not in set(k.type for k in LOADED_KERNELS):
        raise SpiceError('No leap second kernel loaded')


# Concrete loaders for specific file formats
def _load_dummy(path):
    '''Dummy loader for kernels not covered by any other loader.'''
    return {}

def _load_sp(path):
    '''Load sp kernel and associated windows.'''
    _validate_ls()
    _IDS.reset()
    windows = _loader_template_bin(spice.spkobj, spice.spkcov, path)
    for key, vals in windows.items():
        shared.TIMEWINDOWS_POS[key] += vals
    return frozenset(windows.keys())

def _load_c(path):
    '''Load c kernel and associated windows.'''
    _IDS.reset()
    return _loader_template_bin(spice.ckobj, spice.ckcov, path)

def _load_pc(path):
    '''Load pc kernel and associated windows.'''
    _validate_ls()
    _IDS.reset()
    try:
        result = _loader_template_bin(spice.pckfrm, spice.ckcov, path)
    except spice.SpiceError as e:
        # Parse text kernels seperately
        with ignored(IOError):
            result = _loader_template_txt('BODY_?([-0-9]+)_PM', path)
        if result == {}:
            raise e
    return result

def _load_f(path):
    '''Load f kernel.'''
    result = _loader_template_txt('FRAME_?([-0-9]+)_NAME', path)
    if not result:
        msg = 'Empty frame kernel: {}'
        raise spice.SpiceError(msg.format(path))
    return result
