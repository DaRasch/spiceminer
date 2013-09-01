#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import argparse

import re
import urllib
import datetime as dt

from operator import itemgetter


### CONSTANTS ###
NAMES = {'base': {'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/': 'de[0-9]*\.bsp',
                  'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/': 'pck[0-9]*\.tpc',
                  'http://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/': 'naif[0-9]*\.tls'},
         'msl': {}}
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

### Evaluate command line ###
def supported_data(arg):
    if arg.lower() not in NAMES:
        msg = 'DATA must be in {}, was {}.'.format(NAMES.keys(), arg)
        raise argparse.ArgumentTypeError(msg)
    return arg
def valid_path(arg):
    if not os.path.isdir(arg):
        msg = 'PATH {} is not a directory.'.format(arg)
        raise argparse.ArgumentTypeError(msg)
    return arg
parser = argparse.ArgumentParser()
parser.add_argument('data', nargs='*', type=supported_data, default=NAMES.keys(),
    metavar='DATA', help='The data to download (supported: {}).'.format(NAMES.keys()))
parser.add_argument('--dir', '-d', nargs='?', type=valid_path,
    default=BASE_DIR, dest='path', help='Base directory for installation.')
cmdline = parser.parse_args()
print cmdline

### Get data ###
def find_newest(pattern, site):
    regex_time = '[0-9a-zA-Z -]*:[0-9]*'
    regex_fill = '[a-zA-Z<> =/"]*'
    dt_format = '%d-%b-%Y %H:%M'
    choices = re.findall(pattern + regex_fill + regex_time, site)
    choices = [(re.search(pattern, item).group(),
        dt.datetime.strptime(re.search(regex_time, item).group(), dt_format))
        for item in choices]
    return sorted(choices, key=itemgetter(1), reverse=True)[0][0]

def find_old(pattern, dir_path):
    return [name for name in os.listdir(dir_path) if re.search(pattern, name)]

def update(base_dir, name):
    # Prepare directories
    data_dir = os.path.join(base_dir, 'data', name)
    try:
        os.makedirs(data_dir)
    except OSError as e:
        print e
    # Replace old or add new files
    for url, pattern in NAMES[name].iteritems():
        # Get old and new file names
        old_files = find_old(pattern, data_dir)
        site = urllib.urlopen(url)
        newest = find_newest(pattern, site.read())
        site.close()
        # Ignore files if old == new
        if newest in old_files:
            old_files.remove(newest)
        # Download new
        else:
            print '{} >> {}'.format(newest, data_dir)
            with open(os.path.join(data_dir, newest), 'wb') as f:
                download = urllib.urlopen(url + newest)
                f.write(download.read())
                download.close()
        # Remove old
        for f in old_files:
            try:
                os.remove(os.path.join(data_dir, f))
            except OSError as e:
                print e

for name in cmdline.data:
    update(cmdline.path, name)
