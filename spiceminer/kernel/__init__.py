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

    Returns
    -------
    kernels: set of Kernel
        The loaded kernels.

    Raises
    ------
    IOError
        If no files were found.

    See also
    --------
    unload: Unload kernels.
    '''
    return Kernel.load(**locals())

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
    kernels: set of Kernel
        The unloaded kernels.

    See also
    --------
    load: Load files.
    '''
    return Kernel.unload(**locals())
