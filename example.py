#!/usr/bin/env python
#-*- coding:utf-8 -*-

from spiceminer import frange, dtrange, Time, kernel
# Or simply from spiceminer import *. I just like to be explicit

# First load all needed kernels:
kernel.load('../data')

# Next get the object we desire info about:
obj = kernel.get('MARS')
print obj
# Note: if you know the id of the object rather than the name, you can also do:
# kernel.get(499)

# We can get different info from the object, most importantly:
mars_data = obj.get_data(frange(Time(2000), Time(2000, 6), 86400))
print mars_data
# That looks complicated. Let's take a closer look.
# The get_data-method expects an iterable of POSIX timestamps. We need to
# define a time frame for which to obtain data. This is done with ranges like
# this:
# timerange1 = frange(start, stop, step)
# This works for any objects that can be converted to float as for example the
# Time objects.
# If you like datetime too much to accept another time format, you can do this:
# timerange2 = dtrange (datetime1, datetime2, timedelta)

# IMPORTANT: The resulting matrix is ordered like this:
# [time,    time,    time,    time,    time,    time,    time,    time]
# [x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos]
# [y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos]
# [z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos]
# [x_speed, x_speed, x_speed, x_speed, x_speed, x_speed, x_speed, x_speed]
# [y_speed, y_speed, y_speed, y_speed, y_speed, y_speed, y_speed, y_speed]
# [z_speed, z_speed, z_speed, z_speed, z_speed, z_speed, z_speed, z_speed]
