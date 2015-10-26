#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import defaultdict

from .highlevel import Kernel
from .. import _spicewrapper as spice
from .._helpers import ignored

__all__ = ['LOADED_KERNELS', 'LOADED_OBJECTS', 'OBJECTS', 'POS_WINDOWS', 'ROT_WINDOWS']


# Mixins providing functionality for proxy classes
class ProxyContainerMixin:
    def __iter__(self):
        return iter(self._proxy())

    def __len__(self):
        return len(self._proxy())

    def __contains__(self, key):
        return key in self._proxy()

    def __str__(self):
        return str(self._proxy())

    def __repr__(self):
        return repr(self._proxy())


class ProxySequenceMixin(ProxyContainerMixin):
    def __getitem__(self, val):
        return self._proxy()[val]


class ProxyDictMixin(ProxySequenceMixin):
    def iterkeys(self):
        return self._proxy().iterkeys()

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        return self._proxy().itervalues()

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        return self._proxy().iteritems()

    def items(self):
        return list(self.iteritems())


# Concrete Proxy classes
class LoadedKernelProxy(ProxyDictMixin):
    def _proxy(self):
        dct = defaultdict(set)
        for k in Kernel.LOADED:
            dct[k.extension].add(k.path)
        return dct


class LoadedObjectProxy(ProxyContainerMixin):
    def _proxy(self):
        return set.union(set(), *(k.ids for k in Kernel.LOADED))


class ObjectProxy(ProxyDictMixin):
    def _proxy(self):
        result = defaultdict(set)
        for k in Kernel.LOADED:
            result[k.path] = k.ids
        return result


class PosWindowProxy(ProxyDictMixin):
    def _proxy(self):
        return Kernel.TIMEWINDOWS_POS


class RotWindowProxy(ProxyDictMixin):
    def _proxy(self):
        return Kernel.TIMEWINDOWS_ROT


### Actual legacy variables and functions ###

#: (``defaultdict(set)``) -- All loaded kernels, sorted by extension.
LOADED_KERNELS = LoadedKernelProxy()
#: (``set``) -- All loaded Ephimeris Objects. **DEPRECATED**, only for backwards compatibility.
LOADED_OBJECTS = LoadedObjectProxy()
#: (``defaultdict(set)``) -- All loaded Ephimeris Objects sorted by kernel.
OBJECTS = ObjectProxy()
#: (``defaultdict(list)``) -- All time windows for all loaded spk-kernels.
POS_WINDOWS = PosWindowProxy()
#: (``defaultdict(list)``) -- All time windows for all loaded pck/ch-kernels.
ROT_WINDOWS = RotWindowProxy()
