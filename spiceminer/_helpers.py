#-*- coding:utf-8 -*-

from contextlib import contextmanager


@contextmanager
def ignored(exceptions):
    try:
        yield
    except exceptions:
        pass
