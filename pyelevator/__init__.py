# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

version = (0, "5c")

__title__ = "py-elevator"
__author__ = "Oleiade"
__license__ = "MIT"

__version__ = '.'.join(map(str, version))

from .client import Elevator
from .batch import WriteBatch
