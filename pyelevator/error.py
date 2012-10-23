# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import
from .constants import *


class DatabaseError(Exception):
    pass


class SignalError(Exception):
    pass


class TimeoutError(Exception):
    pass


ELEVATOR_ERROR = {
    TYPE_ERROR: TypeError,
    KEY_ERROR: KeyError,
    VALUE_ERROR: ValueError,
    INDEX_ERROR: IndexError,
    RUNTIME_ERROR: RuntimeError,
    OS_ERROR: OSError,
    DATABASE_ERROR: DatabaseError,
    SIGNAL_ERROR: SignalError,
}
