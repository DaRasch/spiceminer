#-*- coding:utf-8 -*-

import os

from contextlib import contextmanager


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def cleanpath(path):
    os.path.abspath(os.realpath(os.path.expanduser(os.path.expandvars(path))))

def iterable_path(path, recursive, followlinks):
    if os.path.isfile(path):
        dirname, basename = os.path.split(path)
        walker = [[dirname, [], [basename]]]
    elif recursive:
        walker = os.walk(path, followlinks=followlinks)
    else:
        walker = [next(os.walk(path, followlinks=followlinks))]
    return walker


class TimeWindow:
    '''A sorted, immutable list of start-end-tuples.
     Necessary for storing information about times for known body
    rotation/position.
    '''
    def __init__(self, *intervals):
        self._raw = list(intervals)
        self._merged = self._merge(self._raw)

    @property
    def raw(self):
        return self._raw[:]

    def __getitem__(self, key):
        return self._merged[key]

    def __iter__(self):
        return iter(self._merged)

    def __str__(self):
        return ''.join([self.__class__.__name__, str(self._merged)])

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self.__class__(*(self.raw + other.raw))

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        lst = self.raw
        for interval in other.raw:
            lst.remove(interval)
        return self.__class__(*lst)

    @staticmethod
    def _merge(lst):
        '''Return a sorted list of non-overlapping start-end-tuples.'''
        if not lst:
            return []
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
