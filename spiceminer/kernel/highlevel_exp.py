#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from . import experimental
from .._helpers import ignored, cleanpath, iterable_path, TimeWindows

__all__ = ['Kernel']


class _KernelMeta(type):
    def __call__(cls, path='.', recursive=True, followlinks=False):
        kmisc, kbody = cls._collect(path, recursive, followlinks)
        if not (kmisc or kbody):
            msg = 'No valid files found on path'
            raise IOError(2, msg, path)
        path_cache = {hash(k): k for k in experimental.LOADED_KERNELS}
        kmisc = set(cls._filter_new(kmisc))
        kbody = set(cls._filter_new(kbody))
        return set.union(kmisc, kbody)

    def _collect(cls, path, recursive, followlinks):
        path = cleanpath(path)
        # Find and sort kernel files.
        body_kernels = {}
        misc_kernels = {}
        for dir_path, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                filepath = os.path.join(dir_path, name)
                with ignored(ValueError):
                    kprops = experimental.kernel_properties(filepath)
                    # Split kernels into those containing bodies and others
                    if kprops.type in experimental.KTYPE_BODY:
                        body_kernels[filepath] = kprops
                    else:
                        misc_kernels[filepath] = kprops
        return misc_kernels, body_kernels

    def _filter_new(cls, cache, dct):
        for path, kprops in dct.items():
            if cache.get(hash(path)) is None:
                yield cls._make(path, kprops)

    def _make(cls, path, kprops):
        kernel = super(cls.__class__, cls).__new__(cls)
        kernel.__init__(path, kprops)
        return kernel


class Kernel(object):
    '''A loaded kernel file.

    .. WARNING:: The constructor should never be used directly. Use one of the
                 methods in the *See also* section.

    Parameters
    ----------
    path: str
        Relative or absolute path to the kernel file/directory.
    kernel_type: {'sp', 'c', 'pc', 'f', 'ls', 'sc'}
        Used to identify what information the kernel is holding and how to load
        it.
    force_reload: bool, optional
        Reload already loaded kernel files.
        By default an error is raised if a kernel file is already loaded.

    Raises
    ------
    ValueError
        If the kernel file is already loaded.

    Attributes
    ----------
    *classattribute* LOADED: set of Kernel
        All loaded kernels.
    *classattribute* TIMEWINDOWS_POS: dict of int -> list
        Maps a list of start-end-tuples for all known time windows of its
        position to the id of a Body.
    *classattribute* TIMEWINDOWS_ROT: dict of int -> list
        Maps a list of start-end-tuples for all known time windows of its
        rotation to the id of a Body.
    path: str
        Absolute path to the kernel file.
    name: str
        Filename of the kernel file.
    type: {'sp', 'c', 'pc', 'f', 'ls', 'sc'}
        Identifier for kernel loading mechanism.
    info: {'pos', 'rot', 'none'}
        What kind of spatial information the kernel contains.
    ids: set of int
        The IDs of all bodies about which the kernel has information.

    See also
    --------
    load: Load multiple files.
    load_single: More controllable way to load single files.
    unload: Unload kernels.
    '''
    LOADED = experimental.LOADED_KERNELS
    TIMEWINDOWS_POS = experimental.TIMEWINDOWS_POS
    TIMEWINDOWS_ROT = experimental.TIMEWINDOWS_ROT

    def __init__(self, path, kprops):
        self.path = path
        self.binary, self.arch, self.type, self.info = kprops
        # Load the kernel file
        self.ids = experimental.load_any(path)
        for id_ in ids:
            Body._make(id_)
        # Make self available for unloading
        self.__class__.LOADED.add(self)

    def _unload(self):
        self.__class__.LOADED.remove(self)
        with ignored(AttributeError):
            windows = self._timewindows()
            for key, vals in self._intervals.iteritems():
                windows[key] -= vals
                if not windows[key]:
                    del windows[key]
        unload_any(self)

    def _timewindows(self):
        windows = 'TIMEWINDOWS_' + self.info.upper()
        return getattr(self.__class__, windows)

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return 'Kernel {} ({})'.format(self.name, self.type)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.path,
            self.experimental.kp(self.binary, self.arch, self.type, self.info))

    @classmethod
    def unload(cls, path='.', recursive=True, followlinks=False):
        '''Unload a kernel file or all kernel files in a directory tree.

        Refer to `spiceminer.unload` for full documentation.

        See also
        --------
        spiceminer.load: Load multiple files.
        spiceminer.load_single: More controllable way to load single files.
        '''
        path = cleanpath(path)
        if not os.path.exists(path):
            msg = 'unload() expected a valid file or directory path, got {}'
            raise ValueError(msg.format(path))
        # Find and sort kernel files.
        hashes = set()
        for dir_path, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                # Ignore extension to be able to unload all kernels
                hashes.add(hash(os.path.join(dir_path, name)))
        # Unload collected kernel files.
        unloaded = {k for k in cls.LOADED if hash(k) in hashes}
        for k in unloaded:
            k._unload()
        return unloaded
