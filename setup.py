#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import glob

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


root_dir = os.path.dirname(os.path.realpath(__file__))
### BUILD C-EXTENSION ###
cspice_root = os.getenv('CSPICEPATH', os.path.join(root_dir, 'cspice'))
if not os.path.isdir(cspice_root):
    print 'ERROR: spice not found' #XXX search lib in default locations?
    sys.exit(1)
cspice_include = os.path.join(cspice_root, 'include')
cspice_lib = os.path.join(cspice_root, 'lib', 'cspice.a') #XXX same under windows?

src_files = glob.glob(os.path.join(root_dir, 'cwrapper', '*.c'))
cwrapper = Extension('spiceminer.libspice', src_files,
    include_dirs=[cspice_include],
    extra_link_args=[cspice_lib])


### METADATA ###
with open(os.path.join(root_dir, 'VERSION')) as f:
    version = f.readline().strip()

with open(os.path.join(root_dir, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(root_dir, 'LICENSE')) as f:
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
    'platforms': 'any',
    'license': license,
    'packages': ['spiceminer'],
    'ext_modules': [cwrapper],
    'requires': ['numpy']
}

if __name__ == '__main__':
    setup(**metadata)
