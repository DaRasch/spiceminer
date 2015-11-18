#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy as np

import spiceminer as sm
from spiceminer.extra import angle

def car2sphere(xyz):
    '''Convert cartesian to spherical coordinates.'''
    r = np.sqrt(np.sum(xyz ** 2, 0))
    theta = np.arccos(xyz[2] / r)
    phi = np.arctan(xyz[1] / xyz[0])
    return r, theta, phi

# Load the necessary data (this example requires parts of the packages 'base'
# and 'msl', which you can download with getdata.py)
sm.load('data')

# Get necessary bodies
mars = sm.Body('mars')
rover = sm.Body('msl_rover')

# Let's look at a month shortly after landing
times = np.arange(sm.Time(2013), sm.Time(2013, 2), sm.Time.HOUR)

# Get position on mars surface
position = rover.position(times, observer=mars, frame=mars)
dist, theta, phi = car2sphere(position[1:])

X, Y, Z = np.identity(3)
# Get the angle of the mars rover on the surface (obvious method)
rotation = rover.rotation(times, target=mars)
rover_x = np.array([r.dot(X) for r in rotation[1]])
rover_y = np.array([r.dot(-Y) for r in rotation[1]])
rover_z = np.array([r.dot(-Z) for r in rotation[1]])
radians = np.array([angle(z, p) for z, p in zip(rover_z, position[1:].T)])
radians_x = np.array([angle(x, p) - np.pi/2 for x, p in zip(rover_x, position[1:].T)])
radians_y = np.array([angle(y, p) - np.pi/2 for y, p in zip(rover_y, position[1:].T)])

# Get the angle of the mars rover on the surface (fast, absolute)
points = mars.position(times, observer=rover, frame=rover)
radians2 = np.array([angle(Z, p) for p in points[1:].T])
radians2_x = np.array([angle(Z[1:], p) for p in points[1::2].T])
radians2_y = np.array([angle(Z[1:], p) for p in points[2:].T])

# Some nice diagrams
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2)
ax = axes[0, 0]
ax.plot(phi, theta, label='position')
ax = axes[1, 0]
ax.plot(dist, label='elevation')
ax = axes[0, 1]
ax.plot(np.degrees(radians), label='Abs')
ax.plot(np.degrees(radians_x), label='X')
ax.plot(np.degrees(radians_y), label='Y')
ax = axes[1, 1]
ax.plot(np.degrees(radians2), label='Abs')
ax.plot(np.degrees(radians2_x), label='X')
ax.plot(np.degrees(radians2_y), label='Y')
for ax in axes.ravel():
    ax.legend()

plt.show(fig)
