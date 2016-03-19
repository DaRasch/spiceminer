#-*- coding:utf-8 -*-

import os

import collections
from contextlib import contextmanager


### Usefull functions ###
@contextmanager
def ignored(*exceptions):
    '''Silence certain exceptions.'''
    try:
        yield
    except exceptions:
        pass

def cleanpath(path):
    '''Make any path absolute.'''
    return os.path.abspath(os.path.realpath(os.path.expanduser(os.path.expandvars(path))))

def iterable_path(path, recursive, followlinks):
    '''Make any path (even if it is a file) walkable with optional recursion.'''
    if os.path.isfile(path):
        dirname, basename = os.path.split(path)
        walker = [[dirname, [], [basename]]]
    elif recursive:
        walker = os.walk(path, followlinks=followlinks)
    else:
        walker = [next(os.walk(path, followlinks=followlinks))]
    return walker


class TimeWindows(collections.Sequence):
    '''A sorted, immutable list of start-end-tuples.
    Necessary for storing information about times for known body
    rotation/position.
    '''
    def __init__(self, *intervals):
        self._raw = list(intervals)
        self._merged = self._merge(self._raw)

    @property
    def raw(self):
        '''A copy of the original data.'''
        return self._raw[:]

    def __getitem__(self, key):
        return self._merged.__getitem__(key)

    def __len__(self):
        return self._merged.__len__()

    # Inherits:
    # __contains__
    # __iter__
    # __reversed__
    # index
    # count

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self._merged)[1:-1])

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            msg = 'can only concatenate {}, got {}'
            raise TypeError(msg.format(self.__class__.__name__, type(other)))
        return self.__class__(*(self.raw + other.raw))

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            msg = 'can only cut {}, got {}'
            raise TypeError(msg.format(self.__class__.__name__, type(other)))
        lst = self.raw
        for interval in other.raw:
            with ignored(ValueError):
                lst.remove(interval)
        return self.__class__(*lst)

    def __eq__(self, other):
        return other == self._merged

    def __bool__(self):
        return bool(self._raw)

    @staticmethod
    def _merge(lst):
        '''Return a sorted list of non-overlapping start-end-tuples.'''
        if not lst:
            return []
        for i, item in enumerate(lst):
            if not isinstance(item, collections.Sequence):
                msg = 'Expected 2-tuples, but arg {} was {}'
                raise TypeError(msg.format(i, item))
            if not len(item) == 2:
                msg = 'Expected 2-tuples, but arg {} was {}'
                raise ValueError(msg.format(i, item))
        lst = iter(sorted(lst))
        result = []
        old = next(lst)
        for new in lst:
            if new[0] > old[1]:
                result.append(old)
                old = new
            else:
                old = (old[0], max(old[1], new[1]))
        result.append(old)
        return result


### Shared variables for Body and Kernel ###
# Mapping of Body -> TimeWindows
TIMEWINDOWS_POS = collections.defaultdict(TimeWindows)
TIMEWINDOWS_ROT = collections.defaultdict(TimeWindows)
