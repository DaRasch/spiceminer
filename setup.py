#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


### BUILD C-EXTENSION ###
cspice_root = os.getenv('CSPICEPATH', 'cspice')
if not os.path.isdir(cspice_root):
    print 'ERROR: spice not found' #XXX search lib in default locations?
    sys.exit(1)
cspice_include = os.path.join(cspice_root, 'include')
cspice_lib = os.path.join(cspice_root, 'lib')

src_files = ['cwrapper/ckgp.c',
            'cwrapper/bodn2c.c',
            'cwrapper/bodc2n.c']
cwrapper = Extension('spiceminer.libspice', src_files,
    include_dirs=[cspice_include],
    library_dirs=[cspice_lib])


### METADATA ###
version = '0.0.1'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

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
