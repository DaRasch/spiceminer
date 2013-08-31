#-*- coding:utf-8 -*-

import os

import spiceminer.kernel as kernel # Bad practice, replace with something that needs not be tested

root_dir = os.path.realpath(os.path.join(__file__, '..', '..'))
data_root = os.getenv('SPICEMINERDATA', os.path.join(root_dir, 'data'))
if not os.path.isdir(data_root):
    msg = 'Data not found. Please read the documentation on tests for more info.'
    raise ImportError(msg)

def load_base():
    kernel.load(data_root, followlinks=True)

