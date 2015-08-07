#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .highlevel import Kernel

# Legacy support (DEPRECATED)
from .legacy_support import *


def load(path='.', recursive=True, followlinks=False):
    return Kernel.load(**locals())

def unload(path='.', recursive=True, followlinks=False):
    return Kernel.unload(**locals())
