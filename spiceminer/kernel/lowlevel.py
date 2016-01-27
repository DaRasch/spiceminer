#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections

from .. import _spicewrapper as spice
from ..time_ import Time
from .._helpers import ignored, TimeWindows


### Constants ###
#TODO: move to constants.py
# File encodings
ARCH_BIN = {'DAF', 'DAS', 'NAIF'}
ARCH_TXT = {'KPL'}
ARCH = set.union(ARCH_BIN, ARCH_TXT)

# Kernel types
KTYPE_POS = {'sp', 'f'}
KTYPE_ROT = {'c', 'pc'}
KTYPE_NONE = {'ls', 'sc', 'i'}
KTYPE_BODY = set.union(KTYPE_POS, KTYPE_ROT)
KTYPE = set.union(KTYPE_BODY, KTYPE_NONE)


### Kernel property parsing ###
# TODO: move to its own module
kp = collections.namedtuple('KernelProperties', ['path', 'binary', 'arch', 'type', 'info'])
def kernel_properties(filepath):
    '''Information about a kernel file.

    Parameters
    ----------
    filepath: str
        Absolute path of a kernel file.

    Raises
    ------
    ValueError
        If the file is not a recognized kernel.

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
    binary = arch in ARCH_BIN
    info = _info_type(kernel_type)
    return kp(filepath, binary, arch, ktype, info)

def _split_identifier(identifier):
    try:
        i = identifier.index('/')
        arch = identifier[:i]
        ktype = identifier[i + 1:][:-1]
    except ValueError:
        arch = identifier[:3]
        ktype = identifier[3:6]
    return arch, ktype

def _info_type(ktype):
    #TODO: unnecessary, remove
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


### Kernel property collection/sorting ###
def icollect_kprops(path, recursive, followlinks):
    '''Find all valid kernel files on path.'''
    for dir_path, _, fnames in iterable_path(path, recursive, followlinks):
        for name in fnames:
            filepath = os.path.join(dir_path, name)
            with ignored(ValueError):
                yield lowlevel.kernel_properties(filepath)

def ifilter_kprops(kprops_iterable):
    '''Yield only new kernels.'''
    existing = {k.path for k in shared.LOADED_KERNELS}
    for kprops in kprops_iterable:
        if kprops.path not in existing:
            yield kprops

def iunload_kprops(kprops_iterable):
    '''Unload kernel, if loaded.'''
    existing = {k.path: k for k in shared.LOADED_KERNELS}
    for kprops in kprops_iterable:
        if kprops.path in existing:
            existing[kprops.path]._unload()
        yield kprops

def split_props(kprops_iterable):
    kpall = set(kprops_iterable)
    kpbody = {p for p in kpall if p.type in lowlevel.KTYPE_BODY}
    kpmisc = kpall - body_kprops
    return kpmisc, kpbody


### Kernel loading ###
def load_any(kprops):
    '''Load any valid kernel file and associated windows if necessary.

    Parameters
    ----------
    kprops: KernelProperties

    Returns
    -------
    window_map: dict[int: list[tuple[Time, Time]]]
        List of time windows for which the transformation information is
        provided, mapped to the respective body id.
    '''
    loader = {
        'sp': _load_sp,
        'c': _load_c,
        'pc': _load_pc,
        'f': _load_f
    }.get(kprops.type, _load_dummy)
    windows = loader(kprops.path)
    spice.furnsh(krops.path)
    return windows

def unload_any(kprops):
    spice.unload(kprops.path)

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
    if 'ls' not in set(k.type for k in shared.LOADED_KERNELS):
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
    return windows

def _load_c(path):
    '''Load c kernel and associated windows.'''
    _IDS.reset()
    windows = _loader_template_bin(spice.ckobj, spice.ckcov, path)
    return windows

def _load_pc(path):
    '''Load pc kernel and associated windows.'''
    _validate_ls()
    _IDS.reset()
    try:
        windows = _loader_template_bin(spice.pckfrm, spice.ckcov, path)
    except spice.SpiceError as e:
        # Parse text kernels seperately
        # TODO: Necessary?
        with ignored(IOError):
            windows = _loader_template_txt('BODY_?([-0-9]+)_PM', path)
        if windows == {}:
            raise e
    return windows

def _load_f(path):
    '''Load f kernel.'''
    windows = _loader_template_txt('FRAME_?([-0-9]+)_NAME', path)
    if not windows:
        msg = 'Empty frame kernel: {}'
        raise spice.SpiceError(msg.format(path))
    return windows
