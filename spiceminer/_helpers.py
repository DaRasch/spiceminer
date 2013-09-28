#-*- coding:utf-8 -*-

from contextlib import contextmanager


@contextmanager
def ignored(exception):
    try:
        yield
    except exception as e:
        pass
