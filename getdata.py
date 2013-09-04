#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import argparse

import re
import pickle
import urllib
import datetime as dt

from operator import itemgetter

# WARNING: This file is ugly and very confusingly written.
# Read on at your own risk.


### CONSTANTS ###
NAMES = {'base': {'generic_kernels/spk/planets/': ['de[0-9]*\.bsp'],
                  'generic_kernels/spk/satellites/': ['mar[0-9]*\.bsp'],
                  'generic_kernels/pck/': ['pck[0-9]*\.tpc'],
                  'generic_kernels/lsk/': ['naif[0-9]*\.tls']},
         'msl': {'MSL/kernels/ck/': ['msl_ra_toolsref_v[0-9]*\.bc',
                                    'msl_cruise_recon_rawrt_v[0-9]*\.bc',
                                    'msl_cruise_recon_raweng_v[0-9]*\.bc',
                                    'msl_edl_v[0-9]*\.bc',
                                    'msl_surf_hga_tlm\.bc',
                                    'msl_surf_ra_tlmenc\.bc',
                                    'msl_surf_ra_tlmres\.bc',
                                    'msl_surf_rsm_tlmenc\.bc',
                                    'msl_surf_rsm_tlmres\.bc',
                                    'msl_surf_rover_tlm\.bc'],
                 'MSL/kernels/fk/': ['msl\.tf'],
                 'MSL/kernels/sclk/': ['msl_lmst_ops[0-9]*_v[0-9]*\.tsc',
                                      'msl.tsc'],
                 'MSL/kernels/spk/': ['msl_struct_v[0-9]*\.bsp',
                                     'mar[0-9]*s\.bsp',
                                     'msl_cruise_v[0-9]*\.bsp',
                                     'msl_edl_v[0-9]*\.bsp',
                                     'msl_ls_ops[0-9]*_iau2000_v[0-9]*\.bsp',
                                     'msl_surf_rover_tlm\.bsp']},
         'helios': {'HELIOS/kernels/spk/': ['[0-9]*R_helios1_[0-9_]*\.bsp',
                                           '[0-9]*R_helios2_[0-9_]*\.bsp']},
         'ulysses': {'ULYSSES/kernels/spk/': ['ulysses_[0-9_]*\.bsp']}}
BASE_URL = 'http://naif.jpl.nasa.gov/pub/naif/'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


### Evaluate command line ###
def supported_data(arg):
    if arg.lower() not in NAMES:
        msg = 'DATA must be in {}, got {}.'.format(NAMES.keys(), arg)
        raise argparse.ArgumentTypeError(msg)
    return arg
def valid_path(arg):
    if not os.path.isdir(arg):
        msg = 'PATH {} is not a directory.'.format(arg)
        raise argparse.ArgumentTypeError(msg)
    return arg
parser = argparse.ArgumentParser()
parser.add_argument('data', nargs='*', type=supported_data,
    default=NAMES.keys(), metavar='DATA',
    help='The data to download (supported: {}).'.format(NAMES.keys()))
parser.add_argument('--dir', '-d', nargs='?', type=valid_path,
    default=BASE_DIR, dest='path', help='Base directory for installation.')
cmdline = parser.parse_args()


### Get data ###
def find_newest(pattern, text):
    '''Returns (name, datetime)'''
    regex_time = '[0-9a-zA-Z -]*:[0-9]*'
    regex_fill = '[a-zA-Z<> =/"]*'
    dt_format = '%d-%b-%Y %H:%M'
    choices = re.findall(pattern + regex_fill + regex_time, text)
    choices = [(re.search(pattern, item).group(),
        dt.datetime.strptime(re.search(regex_time, item).group(), dt_format))
        for item in choices]
    try:
        return sorted(choices, key=itemgetter(1), reverse=True)[0]
    except IndexError:
        print 'Could not match pattern: {}'.format(pattern)

def find_old(pattern, dir_path):
    '''Returns (name, datetime)'''
    time_ = dt.datetime(1970, 1, 1)
    return [(name, time_) for name in os.listdir(dir_path)
        if re.search(pattern, name)]

for name in cmdline.data:
    # Prepare directories
    data_dir = os.path.join(cmdline.path, 'data', name)
    try:
        os.makedirs(data_dir)
    except OSError as e:
        if e.errno != 17:
            print e
            continue
    # Prepare cache
    new_files = []
    old_files = []
    try:
        with open(os.path.join(data_dir, 'metadata.pickle'), 'rb') as f:
            old_files = pickle.load(f)
    except Exception as e:
        print e
        for patterns in NAMES[name].itervalues():
            for pattern in patterns:
                old_files += find_old(pattern, data_dir)
    old_names = [item[0] for item in old_files]
    # Replace old or add new files
    for url, patterns in NAMES[name].iteritems():
        # Get url source text
        site = urllib.urlopen(BASE_URL + url)
        text = site.read()
        site.close()
        # Replace/add
        for pattern in patterns:
            newest = find_newest(pattern, text)
            new_files.append(newest)
            # Handle old files:
            if newest[0] in old_names:
                print '{} exists'.format(newest[0])
                # Ignore if old == new
                if newest in old_files:
                    print '{} is up to date'.format(newest[0])
                    old_files.remove(newest)
                # Remove if old != new
                else:
                    print '{} will be removed'.format(newest[0])
                    try:
                        os.remove(os.path.join(data_dir, newest[0]))
                        old_names.remove(newest[0])
                    except OSError as e:
                        print e
            # Download new
            if newest[0] not in old_names:
                print '{} >> {}'.format(newest[0], data_dir)
                with open(os.path.join(data_dir, newest[0]), 'wb') as f:
                    download = urllib.urlopen(BASE_URL + url + newest[0])
                    f.write(download.read())
                    download.close()
    # Save cache
    with open(os.path.join(data_dir, 'metadata.pickle'), 'wb') as f:
        try:
            pickle.dump(new_files, f)
        except Exception as e:
            print e
