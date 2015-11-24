#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from collections import defaultdict

from .lowlevel import load_any, unload_any, filter_extensions, VALID_BODY_KERNEL_TYPES
from .._helpers import ignored, cleanpath, iterable_path, TimeWindows

__all__ = ['Kernel']


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
    LOADED = set()
    TIMEWINDOWS_POS = defaultdict(TimeWindows)
    TIMEWINDOWS_ROT = defaultdict(TimeWindows)

    def __new__(cls, path, kernel_type, force_reload=False):
        path = cleanpath(path)
        hit = {hash(k): k for k in cls.LOADED}.get(hash(path))
        if hit:
            if not force_reload:
                msg = "Kernel already loaded: {}"
                raise ValueError(msg.format(path))
            else:
                hit._unload()
                return hit
        else:
            return object.__new__(cls)


    def __init__(self, path, kernel_type, force_reload=False):
        self.path = cleanpath(path)
        self.name = os.path.basename(self.path)
        self.type = kernel_type
        # Load the kernel and handle time windows
        self.info, self._intervals = load_any(path, self.type)
        self.ids = frozenset(self._intervals.keys())
        with ignored(AttributeError):
            windows = self._timewindows()
            for key, vals in self._intervals.iteritems():
                windows[key] += vals
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
            self.type)

    @classmethod
    def load(cls, path='.', recursive=True, followlinks=False, force_reload=False):
        '''Load a kernel file or all kernel files in a directory tree.

        Refer to `spiceminer.load` for full documentation.

        See also
        --------
        spiceminer.load_single: More controllable way to load single files.
        spiceminer.unload: Unload kernels.
        '''
        path = cleanpath(path)
        # Find and sort kernel files.
        body_kernels = set()
        misc_kernels = set()
        for dir_path, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                with ignored(ValueError):
                    kernel_type = filter_extensions(name)
                    filepath = os.path.join(dir_path, name)
                    # Split kernels into those containing bodies and others
                    if kernel_type in VALID_BODY_KERNEL_TYPES:
                        body_kernels.add((filepath, kernel_type))
                    else:
                        misc_kernels.add((filepath, kernel_type))
        # Make sure, we actually found at least one valid file.
        if not (body_kernels or misc_kernels):
            msg = 'No valid files found on path'
            raise IOError(2, msg, path)
        # Load collected kernel files (misc first to avoid missing leapseconds).
        loaded = set()
        for path, extension in misc_kernels:
            k = cls(path, extension, force_reload)
            loaded.add(k)
        for path, extension in body_kernels:
            k = cls(path, extension, force_reload)
            loaded.add(k)
        return loaded

    @classmethod
    def load_single(cls, path, extension=None, force_reload=False):
        '''Load a single kernel file. Allows non-standart extensions.

        Refer to `spiceminer.load_single` for full documentation.

        See also
        --------
        spiceminer.load: Load multiple files.
        spiceminer.unload: Unload kernels.
        '''
        if extension is not None:
            kernel_type = filter_extensions('.' + extension)
        else:
            kernel_type = filter_extensions(path)
        k = cls(path, kernel_type, force_reload)
        return k

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
