#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import re
import sys
import argparse

import numpy

import spiceminer as sm
import spiceminer.simple as sms

parser = argparse.ArgumentParser(description='Spice data simulation.')
parser.add_argument('data', type=str,
    help='The directory containing basic planetary data. Needs at least a'
    'leapsecond kernal and a kernel for earth position data.')
parser.add_argument('bodies', nargs='+', metavar='BODY', type=str,
    help='The bodies to simulate and their properties.')
parser.add_argument('-t', '--time', nargs=3, metavar=('START', 'STOP', 'STEPS'), type=str,
    help='The period to simulate. DEFAULT: The last 56 months')
parser.add_argument('-s', '--save', nargs=1, metavar='PATH', type=str,
    help="Don't show the result, but save it.")
parser.add_argument('--title', nargs=1, type=str,
    help="Use a custom title.")
parser.add_argument('--fps', nargs=1, default=[25], type=int,
    help="Set fps. DEFAULT: 25")
ns = parser.parse_args(sys.argv[1:])

def parse_body(item):
    def iparser():
        items = item.split(':')
        yield items[0]
        try:
            props = items[1].split(',')
            for prop in props:
                key, val = prop.split('=')
                try:
                    val = float(val)
                except Exception:
                    pass
                yield key, val
        except IndexError:
            pass
    result = iparser()
    return next(result), dict(result)

bodies = dict(parse_body(body) for body in ns.bodies)
if ns.time:
    start, stop = [sm.Time(*map(int, re.split('[-.: T]', t))) for t in ns.time[:2]]
    step = int(ns.time[2])
    times = numpy.linspace(start, stop, step)
else:
    times = None
anim = sms.SpiceAnimation(ns.data, bodies, times, ns.title or None)

if ns.save:
    writer = [name for name in ('ffmpeg', 'avconv') if name in anim.writers.avail][0]
    anim.save(ns.save[0], writer=anim.writers.avail[writer](fps=ns.fps[0], bitrate=3420))
else:
    anim.show()
