#-*- coding:utf-8 -*-

import os
import re

from collections import defaultdict

import spiceminer._spicewrapper as spice

from .bodies import Body
from .time_ import Time
from ._helpers import ignored

__all__ = ['load', 'unload', 'get', 'LOADED_KERNELS', 'POS_WINDOWS',
    'ROT_WINDOWS']


#: (``defaultdict(set)``) -- All loaded kernels, sorted by extension.
LOADED_KERNELS = defaultdict(set)
#: (``defaultdict(list)``) -- All time windows for all loaded spk-kernels.
POS_WINDOWS = defaultdict(list)
#: (``defaultdict(list)``) -- All time windows for all loaded pck/ch-kernels.
ROT_WINDOWS = defaultdict(list)

_IDS = spice.SpiceCell.integer(1000)
_WINDOWS = spice.SpiceCell.double(100)


### Helpers for load/unload functions ###
def _filter_extensions(filename):
    '''Check for correct extension and return kernel type.'''
    extension = filename.rsplit('.', 1)[1:] or ['']
    match = re.match('(b|t)(s?c|sp|f|ls|pc)$', extension[0])
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
    _IDS.reset()
    spice.spkobj(path, _IDS)
    for idcode in _IDS:
        _WINDOWS.reset()
        spice.spkcov(path, idcode, _WINDOWS)
        # Merge new windows and exsiting windows
        new_windows = [(Time.fromet(et0), Time.fromet(et1))
            for et0, et1 in zip(_WINDOWS[::2], _WINDOWS[1::2])]
        POS_WINDOWS[idcode] = _merge_windows(POS_WINDOWS[idcode] + new_windows)
    return set(_IDS[:])

def _load_c(path):
    '''Load c kernel and associated windows.'''
    _IDS.reset()
    spice.ckobj(path, _IDS)
    for idcode in _IDS:
        _WINDOWS.reset()
        spice.ckcov(path, idcode, _WINDOWS)
        # Merge new windows and exsiting windows
        new_windows = [(Time.fromet(et0), Time.fromet(et1))
            for et0, et1 in zip(_WINDOWS[::2], _WINDOWS[1::2])]
        ROT_WINDOWS[idcode] = _merge_windows(ROT_WINDOWS[idcode] + new_windows)
    return set(_IDS[:])

def _load_pc(path):
    '''Load pc kernel and associated windows.'''
    _IDS.reset()
    try:
        spice.pckfrm(path, _IDS)
        for idcode in _IDS:
            _WINDOWS.reset()
            spice.ckcov(path, idcode, _WINDOWS)
            # Merge new windows and exsiting windows
            new_windows = [(Time.fromet(et0), Time.fromet(et1))
                for et0, et1 in zip(_WINDOWS[::2], _WINDOWS[1::2])]
            ROT_WINDOWS[idcode] = _merge_windows(
                ROT_WINDOWS[idcode] + new_windows)
        return set(_IDS[:])
    except spice.SpiceError:
        # Parse text kernels seperately
        with open(path, 'r') as f:
            return set(map(int, re.findall('BODY([-0-9]*)_PM', f.read())))

def _load_f(path):
    '''Load f kernel.'''
    with open(path, 'r') as f:
        return set(map(int, re.findall('FRAME_([-0-9]*)_NAME', f.read())))

def _load_any(path, extension):
    '''Load **any** file and associated windows if necessary.'''
    loaders = {
        'sp': _load_sp,
        'c': _load_c,
        'pc': _load_pc,
        'f': _load_f
    }
    objects = set()
    with ignored(KeyError):
        objects = loaders[extension](path)
    spice.furnsh(path)
    LOADED_KERNELS[extension].add(path)
    return objects


### Public API ###
def load(path='.', recursive=True, followlinks=False):
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
    :raise: Nothing.

    Meta-kernels are not supported, because they would be parsed internally by
    the c-framework, therefore ignoring the feautures for time window
    extraction.

    At the moment only Ephimeris Objects defined in binary kernels are parsed,
    because of limitations in the c-framework.
    '''
    path = os.path.realpath(path)
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
                # Load kernels with objects later
                if extension in ('sp', 'c', 'pc', 'f'):
                    queue.append((filepath, extension))
                else:
                    queue.insert(0, (filepath, extension))
    loaded_objects = set()
    for filepath, extension in queue:
        objects = _load_any(filepath, extension)
        loaded_objects.update(spice.bodc2n(code) for code in objects)
    with ignored(KeyError):
        loaded_objects.remove(None)
    return loaded_objects

def unload(path='.', recursive=True, followlinks=False):
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
    path = os.path.realpath(path)
    count_unloaded = 0
    if os.path.isfile(path):
        dirname, basename = os.path.split(path)
        walker = [[dirname, [], [basename]]]
    elif recursive:
        walker = os.walk(path, followlinks=followlinks)
    else:
        walker = [next(os.walk(path, followlinks=followlinks))]
    for curdir, dirs, fnames in walker:
        for name in fnames:
            with ignored(ValueError):
                extension = _filter_extensions(name)
                filepath = os.path.join(curdir, name)
                spice.unload(filepath)
                LOADED_KERNELS[extension].remove(filepath)
                count_unloaded += 1
    return count_unloaded

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
