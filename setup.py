#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import glob
import re
import subprocess

try:
    from setuptools import setup, Extension
    from setuptools.command.test import test as Command
    has_setuptools = True
except ImportError:
    from distutils.core import setup, Extension, Command
    has_setuptools = False

PROJECT_NAME = 'spiceminer'

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


### BUILD C-EXTENSION ###
cspice_root = os.getenv('CSPICEPATH', os.path.join(ROOT_DIR, 'cspice'))
if not os.path.isdir(cspice_root):
    print 'ERROR: spice not found' #XXX search lib in default locations?
    sys.exit(1)
cspice_include = os.path.join(cspice_root, 'include')
cspice_lib = os.path.join(cspice_root, 'lib', 'cspice.a') #XXX same under windows?

src_files = glob.glob(os.path.join(ROOT_DIR, 'cwrapper', '*.c'))
cwrapper = Extension('.'.join([PROJECT_NAME, 'libspice']), src_files,
    include_dirs=[cspice_include],
    extra_link_args=[cspice_lib])


### UPDATE TEST BEHAVIOR ###
class NewTestCommand(Command):
    description = 'run test suite'
    user_options = []
    def initialize_options(self):
        self.test_suite = True
    def finalize_options(self):
        pass
    def use_pytest(self):
        import pytest
        errno = pytest.main(self.user_options)
        sys.exit(errno)
    def use_fallback(self):
        test_script = 'runtests.py'
        errno = subprocess.call([sys.executable, test_script])
        sys.exit(errno)
    def run(self):
        setup = os.path.realpath(__file__)
        errno = subprocess.call(
            [sys.executable, setup, 'build_ext', '--inplace'])
        if errno:
            sys.exit(errno)
        try:
            import pytest
            if pytest.__version__ < '2.6.1':
                print('WARNING: Using fallback (pytest version < 2.6.1).')
                self.use_fallback()
            else:
                self.use_pytest()
        except ImportError:
            print('WARNING: Using fallback (pytest not available).')
            self.use_fallback()


### METADATA ###
with open(os.path.join(ROOT_DIR, PROJECT_NAME, '__init__.py')) as f:
    version = re.search("__version__ = '([^']+)'", f.read()).group(1)

with open(os.path.join(ROOT_DIR, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(ROOT_DIR, 'LICENSE')) as f:
    license = f.read()

metadata = {
    'name': PROJECT_NAME,
    'version': version,
    'description': "A sane python wrapper for NASA's SPICE-framework.",
    'long_description': readme,
    'author': 'Philipp Rasch',
    'author_email': 'ph.r@hotmail.de',
    'url': 'https://github.com/DaRasch/spiceminer',
    'download_url': 'https://github.com/DaRasch/spiceminer/archive/master.zip',
    'platforms': 'any',
    'license': license,
    'packages': [PROJECT_NAME],
    'ext_modules': [cwrapper],
    'requires': ['numpy'],
    'cmdclass': {'test': NewTestCommand},
    'classifiers': ('Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: Database',
                     'Topic :: Scientific/Engineering :: Information Analysis')
}

# setuptools only arguments
if has_setuptools:
    metadata.update({
    'tests_require': ['pytest>=2.3']
})


if __name__ == '__main__':
    setup(**metadata)
