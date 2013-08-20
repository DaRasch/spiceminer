#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import platform
import urllib
import StringIO
import zipfile
import subprocess

SYSTEM = ['Cygwin', 'Linux', 'Mac', 'SunOS', 'Windows']
COMPILER = ['Apple C', 'GCC']
PROCESSOR = []
MACHINE = ['32bit', '64bit']

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
print 'Gathering information...'

points = {url: 0 for url in platform_urls}

def give_points(dct, info):
    for key in dct:
        if info in key:
            dct[key] += 1

system = platform.system()
print 'SYSTEM:   ', system
give_points(points, system)

compiler = platform.python_compiler()
print 'COMPILER: ', compiler

processor = platform.processor()
print 'PROCESSOR:', processor

machine = '64bit' if sys.maxsize > 2**32 else '32bit'
print 'MACHINE:  ', machine

result = platform_urls[5] + 'packages/cspice.tar.Z'
print 'Best option:', result.split('/')[0]

### DOWNLOAD AND UNPACK BEST PACKAGE ###
root_dir = os.path.realpath(os.path.dirname(__file__))
archive_path = os.path.join(root_dir, result.split('/')[1])

print '\nDownloading...'
download = urllib.urlopen(root_url + result)

print 'Unpacking...'
if result[:-3] == 'zip':
    filelike = StringIO.StringIO(download.read())
    with zipfile.ZipFile(fileobj=filelike) as archive:
        archive.extractall(root_dir)
    filelike.close()
else:
    cmd = 'gunzip | tar xC ' + root_dir
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
    proc.stdin.write(download.read())
download.close()

print 'Done'
