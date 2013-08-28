#!/usr/bin/env python
#-*- coding:utf-8 -*-

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

import urllib
import re
import datetime as dt

from operator import itemgetter

### Prepare directories ###
root_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__)
if not os.path.isdir(os.path.realpath(root_dir)):
    print 'ERROR: invalid path {}'.format(root_dir)
    sys.exit(1)
data_dir = os.path.join(root_dir, 'data')
try:
    os.mkdir(data_dir)
except OSError:
    pass

### Get old files ###
old_files = [name for name in os.listdir(data_dir) if re.search(
    '\.(bsp|tls|pck)$', name)]

### Download and save files ###
urls = {'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/': 'de[0-9]*\.bsp',
        'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/': 'pck[0-9]*\.tpc',
        'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/': 'naif[0-9]*\.tls'}

def find_newest(pattern, string):
    regex_time = '[0-9a-zA-Z -]*:[0-9]*'
    regex_fill = '[a-zA-Z<> =/"]*'
    dt_format = '%d-%b-%Y %H:%M'
    choices = re.findall(pattern + regex_fill + regex_time, string)
    choices = [(re.search(pattern, item).group(),
        dt.datetime.strptime(re.search(regex_time, item).group(), dt_format))
        for item in choices]
    return sorted(choices, key=itemgetter(1), reverse=True)[0][0]

for url, pattern in urls.iteritems():
    print pattern
    site = urllib.urlopen(url)
    newest = find_newest(pattern, site.read())
    site.close()
    if newest in old_files:
        old_files.remove(newest)
    else:
        with open(os.path.join(data_dir, newest), 'wb') as f:
            print '{} >> {}'.format(newest, data_dir)
            download = urllib.urlopen(url + newest)
            f.write(download.read())
            download.close()

### Remove old files ###
for item in old_files:
    os.remove(os.path.join(data_dir, item))
