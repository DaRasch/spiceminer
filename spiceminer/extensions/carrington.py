#-*- coding:utf-8 -*-

from itertools import izip

import numpy as np

from ..time_ import Time
from ..kernel import get
from ..extra import clockwise_angle, angle, frange

### Helpers ###
_FULL_CIRCLE = 2 * np.pi
# Difference in percentage of full rotation between earth and sun at start time
# (according to spice data)
_DIFF = 0.00894155

### Interesting/Important constants ###
# Carrington rotation number 1 was on 1853-11-9T21:38:45.84
START_TIME = Time(1853, 11, 9) + 0.9019 * Time.DAY
# One rotation takes ~27.2753 days
ROT_PERIOD = (27.2753 * Time.DAY)


### Usefull functions ###
def carr_num(t):
    return 1 + _DIFF + (t - START_TIME) / ROT_PERIOD

def carr_nums(times):
    return np.array([carr_num(t) for t in times])

### Obect dependant functions ###
def carrington_solo(body, start, times, step=Time.HOUR):
    times = list(times)
    pre_times = frange(start, times[0], step)
    pre_pos = body.position(pre_times, observer='SUN')[1:].transpose()
    pre_angle = sum(angle(a, b) for a, b in izip(pre_pos[:-1], pre_pos[1:]))

    pos = body.position(times, observer='SUN')[1:].transpose()
    angles = np.array([0] + [angle(a, b) for a, b in izip(pos[:-1], pos[1:])])
    rot = (angles + pre_angle) / _FULL_CIRCLE
    carrs = carr_nums(times)
    result = carrs + rot
    return result



def carrington_test(body, times):
    x_axis = np.array([1, 0, 0])

    carr = carr_num(times)
    earth_long = clockwise_angle(clockwise_angle(sun.single_rotation(t).dot(
        x_axis)[:2], body.single_position(t)[:2]))
    frac = 1. - earth_long / _FULL_CIRCLE
    n_carr = round(carr_rot - frac)
    diff = carr_rot - frac - n_carr
    carr_rot = n_carr + frac

def carrington_sun(body, times):
    sun = get(10)
    x_axis = np.array([1, 0, 0])
    return np.array([carr_num(t) - (clockwise_angle(sun.single_rotation(t).dot(
        x_axis), body.single_position(t)) / _FULL_CIRCLE) for t in times])

def carrington_sun2(body, times):
    sun = get(10)
    x_axis = np.array([1, 0, 0])
    return np.array([carr_num(t) + (clockwise_angle(sun.single_rotation(t).dot(
        x_axis), body.single_position(t)) / _FULL_CIRCLE) for t in times])

def carrington_sun3(body, times):
    def cut_z(arr):
        arr[2] = 0
        return arr
    x_axis = np.array([1, 0, 0])
    return np.array([carr_num(t) - (angle(x_axis, cut_z(
        body.single_position(t, frame='IAU_SUN'))) / _FULL_CIRCLE) for t in times])


def carrington_idl(body, times):
    if isinstance(body, basestring):
            body = get(body)
    if isinstance(times, float):
            times = [float(times)]

    earth_pos = get(3).position(np.array(times) - 4400 * Time.HOUR)
    positions = body.position(times)

    carr_nums = [(0.5 + (Time.fromposix(t) - START_TIME) / ROT_PERIOD) +
        ((_FULL_CIRCLE - clockwise_angle(pos, epos)) / _FULL_CIRCLE)
        for t, pos, epos in zip(positions[0], positions[1:].T,
            earth_pos[1:].T)]
    return np.array(carr_nums)
