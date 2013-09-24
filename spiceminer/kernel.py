#-*- coding:utf-8 -*-

import os
import re

from collections import defaultdict

import spiceminer._spicewrapper as spice

from .bodies import Body
from .time_ import Time
from ._helpers import ignored

__all__ = ['load', 'unload', 'get']


LOADED_KERNELS = defaultdict(set)
POS_WINDOWS = defaultdict(list)
ROT_WINDOWS = defaultdict(list)

_IDs = spice.SpiceCell.integer(1000)
_WINDOWS = spice.SpiceCell.double(100)


### Helpers for load function ###
def _filter_extensions(filename):
    '''Check for correct extension and return kernel type.'''
    extension = filename.rsplit('.', 1)[1]
    match = re.match('(b|t)(s?c|sp|f|ls|pc)$', extension)
    if match:
        return match.string[1:]
    raise ValueError('Invalid file extension, got {}'.format(extension))

def _merge_windows(lst):
    '''Return a sorted list of non-overlapping start-end-tuples.'''
    if not lst:
        return lst
    lst = sorted(lst)
    tmp = []
    iterator = iter(lst)
    old = next(iterator)
    for new in iterator:
        if new[0] > old[1]:
            tmp.append(old)
            old = new
        else:
            old = (old[0], max(old[1], new[1]))
    tmp.append(old)
    return tmp

def _load_sp(path):
    '''Load sp kernel and associated windows.'''
    _IDs.reset()
    spice.spkobj(path, _IDs)
    for idcode in _IDs:
        _WINDOWS.reset()
        spice.spkcov(path, idcode, _WINDOWS)
        # Merge new windows and exsiting windows
        new_windows = [(Time.fromet(et0), Time.fromet(et1))
            for et0, et1 in zip(_WINDOWS[::2], _WINDOWS[1::2])]
        POS_WINDOWS[idcode] = _merge_windows(POS_WINDOWS[idcode] + new_windows)

def _load_c(path):
    pass

def _load_pc(path):
    pass

def _load_any(path, extension):
    '''Load **any** file and associated windows if necessary.'''
    loaders = {
        'sp': _load_sp,
        'c': _load_c,
        'pc': _load_pc,
    }
    with ignored(KeyError):
        loaders[extension](path)
    spice.furnsh(path)
    LOADED_KERNELS[extension].add(path)


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
    path = os.path.realpath(path)
    count_loaded = 0
    if os.path.isfile(path):
        dirname, basename = os.path.split(path)
        walker = [[dirname, [], [basename]]]
    elif recursive:
        walker = os.walk(path, followlinks=followlinks)
    else:
        walker = [next(os.walk(path, followlinks=followlinks))]
    queue = []
    for curdir, dirs, fnames in walker:
        for name in fnames:
            with ignored(ValueError):
                extension = _filter_extensions(name)
                filepath = os.path.join(curdir, name)
                # load sp, c, pc later
                if extension in ('sp', 'c', 'pc'):
                    queue.append((filepath, extension))
                else:
                    spice.furnsh(filepath)
                    LOADED_KERNELS[extension].add(filepath)
                    count_loaded += 1
    for filepath, extension in queue:
        _load_any(filepath, extension)
        count_loaded += 1
    return count_loaded






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
        path = os.path.realpath(path)
        LOADED_KERNELS.remove(path)
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
            return Body(body_id)
        raise ValueError('get() got invalid name {}.'.format(body))
    with ignored(TypeError):
        return Body(body)
    msg = 'get() integer or str argument expected, got {}.'
    raise TypeError(msg.format(type(body)))
