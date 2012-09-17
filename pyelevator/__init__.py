#!/usr/bin/env python
# -*- coding: utf-8 -*-

version = (0, 0, 1)

__title__ = "py-elevator"
__author__ = "Oleiade"
__license__ = "BSD"

__version__ = '.'.join(map(str, version))

from .elevator import Elevator
from .batch import WriteBatch
