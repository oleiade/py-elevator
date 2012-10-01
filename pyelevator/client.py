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

    def Get(self, key):
        return self.send(self.db_uid, 'GET', [key])

    def MGet(self, keys):
        return self.send(self.db_uid, 'MGET', [keys])

    def Put(self, key, value):
        return self.send(self.db_uid, 'PUT', [key, value])

    def Delete(self, key):
        return self.send(self.db_uid, 'DELETE', [key])

    def Range(self, start=None, limit=None):
        return self.send(self.db_uid, 'RANGE', [start, limit])

    def RangeIter(self, key_from=None, key_to=None):
        range_datas = self.Range(key_from, key_to)
        return RangeIter(range_datas)
