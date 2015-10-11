#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from collections import defaultdict

from .lowlevel import load_any, unload_any, filter_extensions, VALID_BODY_KERNEL_TYPES
from .._helpers import ignored, cleanpath, iterable_path, TimeWindows

__all__ = ['Kernel']


class Kernel(object):
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
        target = ''.join(['TIMEWINDOWS_', self.info.upper()])
        target = getattr(self.__class__, target, None)
        if target is not None:
            for key, vals in self._intervals.iteritems():
                target[key] += vals
        # Make self available for unloading
        self.__class__.LOADED.add(self)

    def _unload(self):
        self.__class__.LOADED.remove(self)
        target = ''.join(['TIMEWINDOWS_', self.info.upper()])
        target = getattr(self.__class__, target, None)
        if target is not None:
            for key, vals in self._intervals.iteritems():
                target[key] -= vals
                if not target[key]:
                    del target[key]
        unload_any(self)

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return 'Kernel {} ({})'.format(self.name, self.type)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.path,
            self.type)

    @classmethod
    def load(cls, path='.', recursive=True, followlinks=False, force_reload=False):
        '''Load a kernel file or a directory containing kernel files.

        :type path: ``str``
        :arg path: Relative or absolute path to the file/(root)directory to load.
        :type recursive: ``bool``
        :arg recursive: If *path* is a directory and *recursive* is ``True``,
          this will also search in child directories and not only the root.
        :type followlinks: ``bool``
        :arg followlinks: If *path* is a directory and *recursive* and
          *followlinks* are both ``True``, symlinked directories further up the
          directory tree will also be traversed.

          .. WARNING:: Setting *followlinks* to ``True`` may lead to infinite
             recursion.

        :return: (``set(str)``) -- The names of all loaded Ephimeris Objects.
        :raise: IOError -- If no files were loaded.

        Meta-kernels are not supported, because they would be parsed internally by
        the c-framework, therefore ignoring the feautures for time window
        extraction.

        At the moment only Ephimeris Objects defined in binary kernels are parsed,
        because of limitations in the c-framework.
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
        ids = set()
        for path, extension in misc_kernels:
            k = cls(path, extension, force_reload)
            ids.update(k.ids)
        for path, extension in body_kernels:
            k = cls(path, extension, force_reload)
            ids.update(k.ids)
        return ids

    @classmethod
    def load_single(cls, path, extension=None, force_reload=False):
        if extension is not None:
            kernel_type = filter_extensions('.' + extension)
        else:
            kernel_type = filter_extensions(path)
        k = cls(path, kernel_type, force_reload)
        return k.ids

    @classmethod
    def unload(cls, path='.', recursive=True, followlinks=False):
        '''Unload a kernel file or a directory containing kernel files.

        :type path: ``str``
        :arg path: Relative or absolute path to the file/(root)directory to unload.
        :type recursive: ``bool``
        :arg recursive: If *path* is a directory and *recursive* is ``True``,
          this will also search in child directories and not only the root.
        :type followlinks: ``bool``
        :arg followlinks: If *path* is a directory and *recursive* and
          *followlinks* are both ``True``, symlinked directories further up the
          directory tree will also be traversed.

          .. WARNING:: Setting *followlinks* to ``True`` may lead to infinite
             recursion.

        :return: (``int``) -- The number of unloaded files.
        :raise: Nothing.

        Time windows are not cleared, since that would require all loaded kernels
        of that type to be checked again
        '''
        path = cleanpath(path)
        if not os.path.exists(path):
            msg = 'unload() expected a valid file or directory path, got {}'
            raise ValueError(msg.format(path))
        # Find and sort kernel files.
        hashes = []
        for dir_path, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                with ignored(ValueError):
                    extension = filter_extensions(name)
                    hashes.append(hash(os.path.join(dir_path, name)))
        # Unload collected kernel files.
        hashmap = {hash(k): k for k in cls.LOADED}
        for key in hashes:
            with ignored(KeyError):
                hashmap[key]._unload()
        return len(hashes)
