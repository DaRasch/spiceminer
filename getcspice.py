#!/usr/bin/env python
#-*- coding:utf-8 -*-

#WARNING: Only tested with Linux 64bit
#TODO: Test with other platforms

from __future__ import print_function

import re
import os
import sys
import platform
import collections

if sys.version_info.major == 3:
    import urllib.request as urllib
    import io as StringIO
    raw_input = input
else:
    import urllib
    import StringIO
import zipfile
import subprocess

root_url = 'http://naif.jpl.nasa.gov/pub/naif/toolkit/C/'
platform_urls = [
    'MacIntel_OSX_AppleC_32bit/',
    'MacIntel_OSX_AppleC_64bit/',
    'MacPPC_OSX_AppleC_32bit/',
    'PC_Cygwin_GCC_32bit/',
    'PC_Linux_GCC_32bit/',
    'PC_Linux_GCC_64bit/',
    'PC_Windows_VisualC_32bit/',
    'PC_Windows_VisualC_64bit/',
    'SunIntel_Solaris_SunC_32bit/',
    'SunIntel_Solaris_SunC_64bit/',
    'SunSPARC_Solaris_GCC_32bit/',
    'SunSPARC_Solaris_GCC_64bit/',
    'SunSPARC_Solaris_SunC_32bit/',
    'SunSPARC_Solaris_SunC_64bit/']

### DETERMINE BEST DOWNLOAD OPTION ###
print('Gathering information...')

points = collections.Counter(platform_urls)

def give_points(dct, info):
    for key in dct:
        if info.lower() in key.lower():
            dct[key] += 1

system = platform.system()
print('SYSTEM:   ', system)
give_points(points, system)

compiler = platform.python_compiler()
compiler = re.search('(Apple|GC|Visual|Sun)C', compiler).group()
print('COMPILER: ', compiler)
give_points(points, compiler)

processor = platform.processor()
print('PROCESSOR:', processor)

machine = '64bit' if sys.maxsize > 2**32 else '32bit'
print('MACHINE:  ', machine)
give_points(points, machine)

def get_winner(dct):
    winner = points.most_common(1)
    return winner[0][0]

result = get_winner(points) + 'packages/cspice.tar.Z'
print('Best option:', result.split('/')[0])

yesno = raw_input('Do you want to download it? [y/n] ')
for char in 'nN':
    if yesno.startswith(char):
        raise SystemExit(0)

### DOWNLOAD AND UNPACK BEST PACKAGE ###
root_dir = os.path.realpath(os.path.dirname(__file__))
archive_path = os.path.join(root_dir, result.split('/')[1])

print('\nDownloading...')
response = urllib.urlopen(root_url + result)
if response.status != 200:
    print('Http error', response.status)
    respons.close()
    raise SystemExit(1)
download = response.read()
response.close()

print('Unpacking...')
if result[:-3] == 'zip':
    filelike = StringIO.StringIO(download)
    with zipfile.ZipFile(fileobj=filelike) as archive:
        archive.extractall(root_dir)
    filelike.close()
else:
    cmd = 'gunzip | tar xC ' + root_dir
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
    proc.stdin.write(download)

print('Done')
