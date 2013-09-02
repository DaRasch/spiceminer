# This example will show the basic usage of the spiceminer module.
from spiceminer import frange, dtrange, Time, kernel
# Or simply from spiceminer import *. I just like to be explicit.

# First we need to load some kernels:
kernel.load('../data')

# Next get the object we desire info about:
obj = kernel.get('MARS')
print obj
print 'Parent:  ', obj.parent()
print 'Children:', obj.children()
# Note: if you know the id of the object rather than the name, you can also
#do: kernel.get(499)

# We also need some time frame to get data from:
start = Time(2000, 1, 1)
stop = Time(2000, 2, 1)
times = frange(start, stop, stop - start)
# The Time-class is similar to the well known datetime but has the advantage
#that it actullay represents POSIX time instead of a date.
# Frange works just like the normal xrange(), the only difference is, that it
#can handle floats.
# Note: the 86400 used as step in this example are 1 day in seconds.

# If you don't want to let go off datetime there is also a range function for
#that:
import datetime
start2 = datetime.datetime(2000, 1, 1)
stop2 = datetime.datetime(2000, 2, 1)
times2 = dtrange(start2, stop2, stop2 - start2)

# Now for the interesting stuff. Getting positional data is pretty easy:
data = obj.state(times)
data2 = obj.state(times2, observer='EARTH')
print data
print data2
# Note: the matrix returned by this method is transposed for easier plotting:
# [time,    time,    time,    time,    time,    time,    time,    time]
# [x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos,   x_pos]
# [y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos,   y_pos]
# [z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos,   z_pos]
# [x_speed, x_speed, x_speed, x_speed, x_speed, x_speed, x_speed, x_speed]
# [y_speed, y_speed, y_speed, y_speed, y_speed, y_speed, y_speed, y_speed]
# [z_speed, z_speed, z_speed, z_speed, z_speed, z_speed, z_speed, z_speed]

# For a real tutorial consult the documentation.
