#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

import spiceminer._spicewrapper as spice
import spiceminer.bodies as bodies

from spiceminer._helpers import ignored

__all__ = ['load', 'unload', 'get', 'LOADED_KERNELS']


LOADED_KERNELS = set()

#TODO enforce resolution of symlinks at all times
def load(path='.', recursive=True, followlinks=False):
    '''Load a kernel file or a directory containing kernel files.

    :type path: ``str``
    :arg path: Relative or absolute path to the file/(root)directory to load.
    :type recursive: ``bool``
    :arg recursive: If ``path`` is a directory and ``recursive`` is ``True``,
      this will also search in child directories and not only the root.
    :type followlinks: ``bool``
    :arg followlinks: If ``path`` is a directory and ``recursive`` and
      ``followlinks`` are both ``True``, symlinked directories further up the
      directory tree will also be traversed.

    .. WARNING:: Setting followlinks to ``True`` may lead to infinite
       recursion.

    :return: (``int``) -- The number of loaded files.
    :raise: Nothing.

    This function will actually try to load **any** file encountered and not
    only valid SPICE-kernel files, possibly slowing down the loading
    process significantly if many and/or big non-kernel files are encountered.
    The return value will also be impacted by this, actually showing the number
    of encountered files, not only kernels.
    '''
    def _loader(path):
        with ignored(spice.SpiceError):
            spice.furnsh(path)
            path = os.path.realpath(path)
            LOADED_KERNELS.add(path)
            return 1
        return 0
    if os.path.isfile(path):
        return _loader(path)
    if not recursive:
        return sum(_loader(os.path.join(path, f))
            for f in next(os.walk(path))[2])
    return sum(sum(_loader(os.path.join(item[0], f)) for f in item[2])
        for item in os.walk(path, followlinks=followlinks))

#TODO enforce resolution of symlinks at all times
def unload(path):
    '''Unload one or more kernel files.

    :type path: ``str``
    :arg path: Relative or absolute path to the file/(root)directory to unload.
      Unloads **all** kernels further up the directory tree if ``path`` is
      a directory.

    :return: (``int``) -- The number of unloaded files.
    :raises: Nothing.
    '''
    def _unloader(path):
        #FIXME fails if different representations of a path are used on load/unload
        LOADED_KERNELS.remove(path)
        path = os.path.realpath(path)
        spice.unload(path)
        return 1
    try:
        _unloader(path)
    except KeyError:
        return sum(_unloader(item)
            for item in tuple(LOADED_KERNELS) if path in item)

def get(body):
    '''Get an entity by name or ID.

    :type body: ``str|int``
    :arg body: Name or ID of the entity to get.

    :return: (:py:class:`~spiceminer.bodies.Body`) -- Representation of the
      requested entity.
    :raises:
      (``ValueError``) -- If the provided name/ID doesn't reference an entity.

      (``TypeError``) -- If ``body`` is neither a string nor an integer.
    '''
    if isinstance(body, basestring):
        body_id = spice.bodn2c(body)
        if body_id is not None:
            return bodies.Body(body_id)
        raise ValueError('get() got invalid name {}.'.format(body))
    with ignored(TypeError):
        return bodies.Body(body)
    msg = 'get() integer or str argument expected, got {}.'
    raise TypeError(msg.format(type(body)))
