#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


# METADATA
version = '0.0.1'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

spice_path = os.path.join(os.getenv('CSPICEPATH', 'cspice'), 'include')
if not os.path.isdir(spice_path):
    print 'ERROR: spice not found' #TODO find library in default locations
    sys.exit(1)

cwrapper = Extension('spiceminer.libspice', ['cwrapper/ckgp.c'],
    include_dirs=[spice_path])

metadata = {
    'name': 'spiceminer',
    'version': version,
    'description': "A sane python wrapper for NASA's SPICE-framework.",
    'long_description': readme,
    'author': 'Philipp Rasch',
    'author_email': 'ph.r@hotmail.de',
    'url': 'https://github.com/DaRasch/spiceminer',
    'download_url': 'https://github.com/DaRasch/spiceminer/archive/master.zip',
    'license': license,
    'packages': ['spiceminer'],
    'ext_modules': [cwrapper],
    'requires': ['numpy']
}

setup(**metadata)
