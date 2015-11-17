#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .highlevel import Kernel


def load(path='.', recursive=True, followlinks=False, force_reload=False):
    '''Load a kernel file or all kernel files in a directory tree.

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
        By default an error is raised if a kernel file is already loaded.

    Returns
    -------
    kernels: set of Kernel
        The loaded kernels.

    Raises
    ------
    IOError
        If no files were loaded.

    See also
    --------
    spiceminer.load_single: More controllable way to load single files.
    spiceminer.unload: Unload kernels.

    Meta-kernels are not supported, because they would be parsed internally by
    the c-framework, therefore ignoring the feautures for time window
    extraction.

    At the moment only Ephimeris Objects defined in binary kernels are parsed,
    because of limitations in the c-framework.
    '''
    return Kernel.load(**locals())

def load_single(cls, path, extension=None, force_reload=False):
    '''Load a single kernel file. Allows non-standart extensions.

    Parameters
    ----------
    path: str
        Relative or absolute path to the kernel file.
    extension: str, optional
        Use the provided extension instead of the extension of the file.
    force_reload: bool, optional
        Reload already loaded kernel files.
        By default an error is raised if a kernel file is already loaded.

    Returns
    -------
    Kernel
        The loaded kernel.

    Raises
    ------
    IOError
        If no files were loaded.

    See also
    --------
    spiceminer.load: Load multiple files.
    spiceminer.unload: Unload kernels.
    '''
    return Kernel.load_single(**locals())

def unload(path='.', recursive=True, followlinks=False):
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
    int
        Number of unloaded kernels.

    See also
    --------
    spiceminer.load: Load multiple files.
    spiceminer.load_single: More controllable way to load single files.
    '''
    return Kernel.unload(**locals())
