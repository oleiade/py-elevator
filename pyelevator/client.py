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
        return self.send(self.db_uid, 'GET', [key], *args, **kwargs)

    def MGet(self, keys, *args, **kwargs):
        fill_cache = kwargs.pop('fill_cache', False)
        return self.send(self.db_uid, 'MGET', [keys, fill_cache], *args, **kwargs)

    def Put(self, key, value, *args, **kwargs):
        return self.send(self.db_uid, 'PUT', [key, value], *args, **kwargs)

    def Delete(self, key, *args, **kwargs):
        return self.send(self.db_uid, 'DELETE', [key], *args, **kwargs)

    def Range(self, *args, **kwargs):
        start = kwargs.pop('start', None)
        limit = kwargs.pop('limit', None)
        return self.send(self.db_uid, 'RANGE', [start, limit], *args, **kwargs)

    def RangeIter(self, key_from=None, key_to=None, *args, **kwargs):
        range_datas = self.Range(key_from, key_to)
        return RangeIter(range_datas)
