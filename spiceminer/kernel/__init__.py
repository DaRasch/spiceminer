#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .highlevel import Kernel


def load(path='.', recursive=True, followlinks=False, force_reload=False):
    return Kernel.load(**locals())

def load_single(cls, path, extension=None, force_reload=False):
    return Kernel.load_single(**locals())

def unload(path='.', recursive=True, followlinks=False):
    return Kernel.unload(**locals())
