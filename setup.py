#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import platform
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# METADATA
version = '0.0.1'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

metadata = {
    'name': 'spiceminer',
    'version': version,
    'description': "A sane Python wrapper for NASA's SPICE-framework.",
    'long_description': readme,
    'author': 'Philipp Rasch',
    'author_email': 'ph.r@hotmail.de',
    'url': 'https://github.com/DaRasch/spiceminer',
    'download_url': 'https://github.com/DaRasch/spiceminer/archive/master.zip',
    'license': license,
    'packages': ['spiceminer']
}

# COMMANDLINE HANDLING
if 'build' in sys.argv[1:]:
    sourcefiles = ['ckgp.c']
    system = platform.system()
    root = os.path.dirname(__file__)
    # Check for cspice location
    spice_path = os.getenv('CSPICEPATH', os.path.join(root, 'cspice'))
    if not os.path.isdir(spice_path):
        print 'ERROR: spice not found'
    # Get other relevant paths
    header_path = os.path.join(spice_path, 'include')
    src_path = os.path.join(root, 'cwrapper')
    # Compile so or dll
    if system == 'Linux':
        commandline = ['gcc', '-Wall', '-Werror', '-c', '-I' + header_path,
        '-fPIC'] + [os.path.join(src_path, f) for f in sourcefiles]
        try:
            print subprocess.check_output(commandline) or 'gcc: objects built' #TODO check errors
        except: pass
        objectfiles = [f for f in os.listdir(src_path) if f.endswith('.o')]
        commandline = ['gcc', '-Wall', '-Werror', '-shared', '-o',
            os.path.join(root, 'spiceminer', '_libspicewrapper.so')] + objectfiles
        try:
            print subprocess.check_output(commandline) or 'gcc: lib built' #TODO check errors
        except: pass
    else: #TODO make platform independent
        raise NotImplementedError('OS not supported')
    # Clean up after build
    for name in os.listdir(src_path):
        if name.endswith('.o'):
            os.remove(name)


else:
    setup(**metadata)
