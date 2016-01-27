#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import itertools

from . import shared
from . import lowlevel
from .. import bodies
from .._helpers import ignored, cleanpath, iterable_path

__all__ = ['Kernel']

class _KernelMeta(type):
    '''Type for Kernel.

    Allows better abstraction between instance cration and cacheing.
    '''

    def __call__(cls, path='.', recursive=True, followlinks=False, force=False):
        '''Load kernels from path.'''
        path = cleanpath(path)
        if not os.path.exists(path):
            msg = 'No such file or directory'
            raise IOError(2, msg, path)
        kpall = lowlevel.icollect_kprops(path, recursive, followlinks)
        # Raise error if iterator is empty
        try:
            first = next(iterable)
        except StopIteration:
            msg = 'No valid files found on path'
            raise IOError(2, msg, path)
        else:
            kpall = itertools.chain([first], iterable)
        # Filter depending on force to allow reloading existing kernels
        if force:
            kpall = lowlevel.iunload_kprops(kpall)
        else:
            kpall = lowlevel.ifilter_kprops(kpall)
        # Split and create instances (misc first, to assure .tls is loaded)
        kpmisc, kpbody = lowlevel.split_props(kpall)
        misc_kernels = set(cls._make(kprops) for kprops in kpmisc)
        body_kernels = set(cls._make(kprops) for kprops in kpbody)
        return set.union(misc_kernels, body_kernels)

    def _make(cls, kprops):
        '''Create new instance.'''
        kernel = super(cls.__class__, cls).__new__(cls)
        kernel.__init__(kprops)
        return kernel


class Kernel(object):
    '''A loaded kernel file.

    Meta-kernels are not supported, because they would be parsed internally by
    the C-framework, therefore ignoring the feautures for time window
    extraction.

    Parameters
    ----------
    path: str, optional
        Relative or absolute path to the kernel file/directory.
    recursive: bool, optional
        Search subdirectories for kernel files.
    followlinks: bool, optional
        Follow symbolic links.
    force_reload: bool, optional
        Reload already loaded kernel files.

    Returns
    -------
    kernels: set of Kernel
        The loaded kernels.

    Raises
    ------
    IOError
        If no files were found.

    Attributes
    ----------
    *classattribute* LOADED: set of Kernel
        All loaded kernels.
    *classattribute* TIMEWINDOWS_POS: dict of Body -> list
        Maps a list of start-end-tuples for all known time windows of its
        position to a Body.
    *classattribute* TIMEWINDOWS_ROT: dict of Body -> list
        Maps a list of start-end-tuples for all known time windows of its
        rotation to a Body.
    path: str
        Absolute path to the kernel file.
    binary: bool
        Wether the kernel file is encoded in binary or ascii.
    arch: {'DAF', 'DAS', 'NAIF', 'KPL'}
        The storage format of the kernel file.
    type: {'sp', 'c', 'pc', 'f', 'ls', 'sc', 'i'}
        Identifier for kernel loading mechanism.
    info: {'pos', 'rot', 'none'}
        What kind of spatial information the kernel contains.
    bodies: set of Body
        All bodies about which the kernel has information.

    See also
    --------
    Kernel.unload: Unload kernels.
    '''

    __metaclass__ = _KernelMeta

    LOADED = shared.LOADED_KERNELS
    TIMEWINDOWS_POS = shared.TIMEWINDOWS_POS
    TIMEWINDOWS_ROT = shared.TIMEWINDOWS_ROT

    def __init__(self, kprops):
        self.path, self.binary, self.arch, self.type, self.info = kprops
        self.bodies = set()
        # Load the kernel file
        self._windows = lowlevel.load_any(path)
        for _id, vals in self._windows.items():
            body = bodies.Body._make(id_)
            self.bodies.add(body)
            if self.type in lowlevel.KTYPE_POS:
                Kernel.TIMEWINDOWS_POS[body] += vals
            elif self.type in lowlevel.KTYPE_ROT:
                Kernel.TIMEWINDOWS_ROT[body] += vals
        # Make self available for unloading
        self.__class__.LOADED.add(self)

    def _unload(self):
        self.__class__.LOADED.remove(self)
        if self.type in lowlevel.KTYPE_BODY:
            if self.type in lowlevel.KTYPE_POS:
                windows = Kernel.TIMEWINDOWS_POS
            elif self.type in lowlevel.KTYPE_ROT:
                windows = Kernel.TIMEWINDOWS_ROT
            for _id, vals in self._windows.items():
                body = bodies.Body(id_)
                windows[body] -= vals
                if not windows[body]:
                    del windows[body]
                bodies.Body._delete(id_)
        lowlevel.unload_any(self.kprops)

    def __str__(self):
        return '{} {} ({})'.format(
            self.__class__.__name__, os.path.basename(self.path), self.type)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.path)

    @classmethod
    def unload(cls, path='.', recursive=True, followlinks=False):
        '''Unload a kernel file or all kernel files in a directory tree.

        Parameters
        ----------
        path: str, optional
            Relative or absolute path to the kernel file/directory.
        recursive: bool, optional
            Search subdirectories for kernel files.
        followlinks: bool, optional
            Follow symbolic links.

        Returns
        -------
        kernels: set of kernel
            The unloaded kernels.

        See also
        --------
        Kernel: Load files.
        '''
        path = cleanpath(path)
        if not os.path.exists(path):
            msg = 'No such file or directory'
            raise IOError(2, msg, path)
        kpfound = set.union(*cls._collect(path, recursive, followlinks))
        if not kpfound:
            msg = 'No valid files found on path'
            raise IOError(2, msg, path)
        kpfound = {p.path for p in kpfound}
        kernels = {k for k in cls.LOADED if k.path in kpfound}
        # FIXME: Unload ls kernel last and only if no more bodies are loaded
        for k in kernels:
            k._unload()
        return kernels
