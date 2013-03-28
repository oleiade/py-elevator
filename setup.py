#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('pyelevator').__version__

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name='py-elevator',
    version=version,
    license='MIT',

    description = 'Python client for on-disk key/value database Elevator',
    long_description=README,

    author='Oleiade',
    author_email='tcrevon@gmail.com',
    url='http://github.com/oleiade/py-elevator',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ],
    keywords='py-elevator elevator leveldb database key-value',

    packages=[
        'pyelevator',
        'pyelevator.utils',
    ],
    package_dir={'': '.'},
    include_package_data=False,

    install_requires=[
        'pyzmq==13.0.2',
        'lz4',
        'msgpack-python'
    ],
)
