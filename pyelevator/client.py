# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from .base import Client


class RangeIter(object):
    def __init__(self, range_datas):
        self._container = range_datas if self._valid_range(range_datas) else None

    def _valid_range(self, range_datas):
        if range_datas and (not isinstance(range_datas, (list, tuple)) or
            any(not isinstance(pair, (list, tuple)) for pair in range_datas)):
            raise ValueError("Range datas format not recognized")
        return True

    def __iter__(self):
        return self.forward()

    def forward(self):
        current_item = 0
        while (current_item < len(self._container)):
            container = self._container[current_item]
            current_item += 1
            yield container


class Elevator(Client):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def Get(self, key, *args, **kwargs):
        datas = self.send(self.db_uid, 'GET', [key], *args, **kwargs)
        return datas[0]

    def MGet(self, keys, *args, **kwargs):
        return self.send(self.db_uid, 'MGET', [keys], *args, **kwargs)

    def Put(self, key, value, *args, **kwargs):
        self.send(self.db_uid, 'PUT', [key, value], *args, **kwargs)
        return

    def Delete(self, key, *args, **kwargs):
        self.send(self.db_uid, 'DELETE', [key], *args, **kwargs)
        return

    def Range(self, start=None, limit=None, *args, **kwargs):
        return self.send(self.db_uid, 'RANGE', [start, limit], *args, **kwargs)

    def Slice(self, key_from=None, offset=None, *args, **kwargs):
        return self.send(self.db_uid, 'SLICE', [key_from, offset], *args, **kwargs)

    def RangeIter(self, key_from=None, key_to=None, *args, **kwargs):
        cmd = self.Range if isinstance(key_to, str) else self.Slice
        range_datas = cmd(key_from, key_to)
        return RangeIter(range_datas)
