#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('pyelevator').__version__

with open(os.path.join(root, 'README.md')) as f:
    README = f.read()

setup(
    name='py-elevator',
    version=version,
    license='BSD',

    description = 'Python client for key/value database Elevator',
    long_description=README,

    author='Oleiade',
    author_email='tcrevon@gmail.com',
    url='http://github.com/oleiade/py-elevator',

    classifiers=[
        'Development Status :: 0.0.1',
        'Environment :: Unix-like Systems',
        'Programming Language :: Python',
        'Operating System :: Unix-like',
    ],
    keywords='py-elevator elevator leveldb database key-value',

    packages=[
        'pyelevator',
    ],
    package_dir={'': '.'},

    install_requires=[
        'pyzmq>=2.1.11',
        'msgpack-python'
    ],
)