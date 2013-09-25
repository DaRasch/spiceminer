#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import glob

try:
    from setuptools import setup, Extension
    from setuptools.command.test import test as Command
    has_setuptools = True
except ImportError:
    from distutils.core import setup, Extension, Command
    has_setuptools = False


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


### UPDATE TEST BEHAVIOR ###
try:
    import pytest
    has_pytest = True
except ImportError:
    has_pytest = False

if has_setuptools:
    class NewTestCommand(Command):
        def finalize_options(self):
            Command.finalize_options(self)
            self.test_args = []
            self.test_suite = True
        def run_tests(self):
            # import here, cause outside the eggs aren't loaded
            import pytest
            errno = pytest.main(self.test_args)
            sys.exit(errno)
else:
    class NewTestCommand(Command):
        user_options = []
        def initialize_options(self):
            pass
        def finalize_options(self):
            pass
        def run_default(self):
            import pytest
            if pytest.__version__ < '2.3':
                print 'WARNING: pytest version must be >= 2.3'
                self.run_fallback()
            errno = pytest.main(self.user_options)
            sys.exit(errno)
        def run_fallback(self):
            import subprocess
            test_script = os.path.join(root_dir, 'test', 'runtests.py')
            #TODO call setup.py egg_info, setup.py build_ext --inplace
            errno = subprocess.call([sys.executable, test_script])
            raise SystemExit(errno)
        def run(self):
            try:
                self.run_default()
            except ImportError:
                self.run_fallback()


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
