#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .highlevel import Kernel


def load(path='.', recursive=True, followlinks=False, force_reload=False):
    '''Load a kernel file or all kernel files in a directory tree.

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
        By default an error is raised if a kernel file is already loaded.

    Returns
    -------
    kernels: set of Kernel
        The loaded kernels.

    Raises
    ------
    ValueError
        If the kernel file is already loaded.
    IOError
        If no files were loaded.

    See also
    --------
    load_single: More controllable way to load single files.
    unload: Unload kernels.
    '''
    return Kernel.load(**locals())

def load_single(path, extension=None, force_reload=False):
    '''Load a single kernel file. Allows non-standart extensions.

    Meta-kernels are not supported, because they would be parsed internally by
    the C-framework, therefore ignoring the feautures for time window
    extraction.

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
    ValueError
        If the kernel file is already loaded.
    IOError
        If no files were loaded.

    See also
    --------
    load: Load multiple files.
    unload: Unload kernels.
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
    kernels: set of kernel
        The unloaded kernels.

    See also
    --------
    load: Load multiple files.
    load_single: More controllable way to load single files.
    '''
    return Kernel.unload(**locals())
