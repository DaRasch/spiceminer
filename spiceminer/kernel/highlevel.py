#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from collections import defaultdict

from .lowlevel import load_any, unload_any, filter_extensions, VALID_BODY_KERNEL_TYPES
from .._helpers import ignored, cleanpath, iterable_path, TimeWindows

__all__ = ['Kernel']


class Kernel:
    LOADED = set()
    TIMEWINDOWS_POS = defaultdict(TimeWindows)
    TIMEWINDOWS_ROT = defaultdict(TimeWindows)

    def __init__(self, path, extension, force_reload=False):
        self.path = cleanpath(path)
        self.name = os.path.basename(self.path)
        self.extension = extension
        # Make sure this kernel is not already loaded.
        if hash(self) in (hash(k) for k in self.__class__.LOADED) and not force_reload:
            msg = "Kernel with name '{}' and extension '{}' is already loaded"
            raise ValueError(msg.format(self.name, self.extension))
        # Load the kernel and handle time windows
        self.type, self._intervals = load_any(path, extension)
        self.ids = frozenset(self._intervals.keys())
        if self.type == 'pos':
            dest = self.__class__.TIMEWINDOWS_POS
        elif self.type == 'rot':
            dest = self.__class__.TIMEWINDOWS_ROT
        for key, vals in self._intervals.iteritems():
            dest[key] += vals
        # Make self available for unloading
        self.__class__.LOADED.add(self)

    def _unload(self):
        self.__class__.LOADED.remove(self)
        if self.type == 'pos':
            dest = self.__class__.TIMEWINDOWS_POS
        elif self.type == 'rot':
            dest = self.__class__.TIMEWINDOWS_ROT
        for key, vals in self._intervals:
            dest[key] -= val
        unload_any(self)

    def __hash__(self):
        return hash(''.join([self.name, self.extension]))

    def __str__(self):
        return 'Kernel {} ({})'.format(self.name, self.extension)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.path,
            self.extension)

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
        if not os.path.exists(path):
            msg = 'load() expected a valid file or directory path, got {}'
            raise ValueError(msg.format(path))
        # Find and sort kernel files.
        body_kernels = []
        misc_kernels = []
        for curdir, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                with ignored(ValueError):
                    extension = filter_extensions(name)
                    filepath = os.path.join(curdir, name)
                    # Split kernels into those containing bodies and others
                    if extension in VALID_BODY_KERNEL_TYPES:
                        body_kernels.append((filepath, extension))
                    else:
                        misc_kernels.append((filepath, extension))
        # Make sure, we actually found at least one valid file.
        if not (body_kernels or misc_kernels):
            msg = 'No valid files found on path {}'
            raise IOError(2, msg.format(path))
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
        path = cleanpath(path)
        if not os.path.isfile(path):
            msg = 'load_single() expected a file path, got {}'
            raise ValueError(msg.format(path))
        if extension is not None:
            extension = filter_extensions('.' + extension)
        else:
            extension = filter_extensions(path)
        k = cls(path, extension, force_reload)
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
        for _, _, fnames in iterable_path(path, recursive, followlinks):
            for name in fnames:
                with ignored(ValueError):
                    extension = filter_extensions(name)
                    hashes.append(hash(''.join([name, extension])))
        # Unload collected kernel files.
        hashmap = {hash(k): k for k in cls.LOADED}
        for key in hashes:
            hashmap[key]._unload()
        return len(hashes)
