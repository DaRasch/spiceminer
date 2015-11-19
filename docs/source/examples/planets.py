#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy as np

import spiceminer as sm

# Load the necessary data (this example requires parts of the package 'base',
# which you can download with getdata.py)
sm.load('data')

# Get some planets and moons
mercury = sm.Body('mercury')
venus = sm.Body('venus')
earth = sm.Body('earth')
moon = sm.Body('moon')
mars = sm.Body('mars')

# Get position information for 2 years
times = np.arange(sm.Time(2000), sm.Time(2002), sm.Time.DAY)
mercury_pos = mercury.position(times)
venus_pos = venus.position(times)
earth_pos = earth.position(times)
moon_pos = moon.position(times)
mars_pos = mars.position(times)

# Plot them (the moon is only visible if you zoom in close)
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1)
ax = axes
ax.plot(*mercury_pos[1:3], label=mercury.name)
ax.plot(*venus_pos[1:3], label=venus.name)
ax.plot(*earth_pos[1:3], label=earth.name)
ax.plot(*moon_pos[1:3], label=moon.name)
ax.plot(*mars_pos[1:3], label=mars.name)
ax.grid()
ax.legend()
plt.show(fig)
