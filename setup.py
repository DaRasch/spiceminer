#!/usr/bin/env python
#-*- coding:utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.0.1'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='spiceminer',
    version=version,
    description="A sane Python wrapper for NASA's SPICE-framework.",
    long_description=readme,
    author='Philipp Rasch',
    author_email='ph.r@hotmail.de',
    url='https://github.com/DaRasch/spiceminer',
    download_url='https://github.com/DaRasch/spiceminer/archive/master.zip',
    license=license,
    packages=['spiceminer']
)
