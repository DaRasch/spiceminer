#!/usr/bin/env python
#-*- coding:utf-8 -*-

import collections


def _is_binary(sample):
    for char in sample:
        if not ((32 <= ord(char) <= 126) or ord(cahr) == 9):
            return True
            break
    else:
        return False

def _split_identifier(identifier):
    architecture = identifier[:3]
    if '/' in identifier:
        kernel_type = identifier[4:][:-1]
    else:
        kernel_type = identifier[3:6]
    return architecture, kernel_type

def _info_type(kernel_type):
    if kernel_type in {'sp', 'f'}:
        return 'pos'
    elif kernel_type in {'c', 'pc'}:
        return 'rot'
    else:
        return 'none'

kp = collections.namedtuple('KernelProperties', 'binary', 'arch', 'type', 'info')
def kernel_properties(filepath):
    '''Collect kernel properties.

    Notes
    -----
    Identifier description:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#SPICE%20Kernel%20Type%20Identification
    Legal characters in text kernels:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#Text%20Kernel%20Specifications
    '''
    with open(filepath, 'rb') as file:
        identifier = file.read(8).strip()
        sample = file.read(16)
    binary = _is_binary(sample)
    architecture, kernel_type = _split_identifier(identifier)
    info_type = _info_type(kernel_type)
    return kp(binary, architecture, kernel_type, info_type)

