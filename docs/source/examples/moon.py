#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy as np

import spiceminer as sm

# Load the necessary data (this example requires parts of the package 'base',
# which you can download with getdata.py)
sm.load('data')

# Get some planets and moons
moon = sm.Body('moon')

# Get position information for a month
times = np.arange(sm.Time(2000), sm.Time(2000, 2), sm.Time.DAY)
moon_pos1 = moon.position(times, observer='earth')
moon_pos2 = moon.position(times, observer='earth', frame='earth')

# Plot them
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2)
ax = axes[0]
ax.plot(*moon_pos1[1:3], label='Frame ECLIPJ2000')
ax = axes[1]
ax.plot(*moon_pos2[1:3], label='Frame EARTH')
for ax in axes.ravel():
    ax.grid()
    ax.legend()
plt.show(fig)
