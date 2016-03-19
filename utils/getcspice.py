#!/usr/bin/env python
#-*- coding:utf-8 -*-

#WARNING: Only tested with Linux 64bit and Windows 10 64bit
#TODO: Test with other platforms

from __future__ import print_function

import re
import os
import sys
import platform
import contextlib
import subprocess
import collections

if sys.version_info.major == 3:
    import urllib.request as urllib
    import io
    raw_input = input
else:
    import urllib2 as urllib
    import io
import zipfile
import tarfile


def best_fit(options):
    options = collections.Counter(options)

    def give_points(info):
        for key in options:
            if info.lower() in key.lower():
                options[key] += 1

    print('Gathering information...')

    system = platform.system()
    print('  SYSTEM:   ', system)
    give_points(system)

    compiler = platform.python_compiler()
    compiler = re.search('(Apple|GC|Visual|MS|Sun)C', compiler).group()
    print('  COMPILER: ', compiler)
    give_points(compiler)

    processor = platform.processor()
    print('  PROCESSOR:', processor)
    give_points(processor)

    machine = '64bit' if sys.maxsize > 2**32 else '32bit'
    print('  MACHINE:  ', machine)
    give_points(machine)

    winner = options.most_common(1)[0][0]
    print('Best option:', winner)
    return winner


def download(url, chunksize=2**20):
    def _ipercentage(size):
        chunks = 1
        yield '{:0>6.2f}%'.format(0)
        while True:
            percentage = min(100, 100.0 * chunks * chunksize / size)
            yield '{}{:0>6.2f}%'.format('\b' * 7, percentage)
            chunks += 1

    def _ianimation():
        animation = '.:.....'
        yield animation
        while True:
            animation = ''.join(['\b' * 7, animation[1:], animation[:-1]])
            yield animation

    print('Downloading: {}'.format(url))
    # Open url
    response = urllib.urlopen(url)
    with contextlib.closing(response):
         # Validate response
        if response.code != 200:
            print('Http error', response.msg)
            raise SystemExit(1)
        # Generate progress indicator
        try:
            size = int(response.headers['content-length'])
            visual_provider = _ipercentage(size)
        except KeyError:
            visual_provider = _ianimation()
        # Download
        fakefile = io.BytesIO()
        print(next(visual_provider), end='')
        sys.stdout.flush()
        while True:
            chunk = response.read(chunksize)
            if not chunk:
                break
            fakefile.write(chunk)
            print(next(visual_provider), end='')
            sys.stdout.flush()
        print()
    fakefile.seek(0)
    return fakefile


def unpack(filelike, path, zip):
    print('Unpacking to: {}'.format(path))
    if zip:
        zipfile.ZipFile(filelike).extractall(path)
    else:
        cmd = 'gunzip | tar xC ' + path
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
        proc.stdin.write(filelike.read())


def main(path=None, yesno=None):
    ROOT_URL = 'http://naif.jpl.nasa.gov/pub/naif/toolkit/C'
    PLATFORM_URLS = [
        'MacIntel_OSX_AppleC_32bit',
        'MacIntel_OSX_AppleC_64bit',
        'MacPPC_OSX_AppleC_32bit',
        'PC_Cygwin_GCC_32bit',
        'PC_Linux_GCC_32bit',
        'PC_Linux_GCC_64bit',
        'PC_Windows_VisualC_32bit',
        'PC_Windows_VisualC_64bit',
        'SunIntel_Solaris_SunC_32bit',
        'SunIntel_Solaris_SunC_64bit',
        'SunSPARC_Solaris_GCC_32bit',
        'SunSPARC_Solaris_GCC_64bit',
        'SunSPARC_Solaris_SunC_32bit',
        'SunSPARC_Solaris_SunC_64bit']

    platform_url = best_fit(PLATFORM_URLS)
    use_zip = platform_url.startswith('PC_Windows')
    file_url = 'packages/cspice{0}'.format(('.zip' if use_zip else '.tar.Z'))

    result = '/'.join([ROOT_URL, platform_url, file_url])

    if yesno is None:
        yesno = raw_input('Do you want to download it? [y/n] ')
        for char in 'nN':
            if yesno.startswith(char):
                raise SystemExit(0)
    elif not yesno:
        raise SystemExit(0)

    ### DOWNLOAD AND UNPACK BEST PACKAGE ###
    ROOT_DIR = path or os.path.realpath(os.path.dirname(__file__))

    filelike = download(result)
    with contextlib.closing(filelike):
        unpack(filelike, ROOT_DIR, use_zip)

    print('Done')


if __name__ == '__main__':
    main()
