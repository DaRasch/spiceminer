#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections

from ._helpers import TimeWindows


# Set of Kernel
LOADED_KERNELS = set()

# Mapping of Body -> TimeWindows
TIMEWINDOWS_POS = collections.defaultdict(TimeWindows)
TIMEWINDOWS_ROT = collections.defaultdict(TimeWindows)
