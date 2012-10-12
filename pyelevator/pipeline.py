from __future__ import absolute_import

from .base import Client


class Pipeline(Client):
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)
        self.queue = []

    def _action_request(self, command, *args):
        return {
            'COMMAND': command,
            'ARGS': args,
        }

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.execute()

    def Get(self, key, *args, **kwargs):
        self.queue.append(self._action_request("GET", key))

    def MGet(self, keys, *args, **kwargs):
        self.queue.append(self.action_request("MGET", keys))

    def Put(self, key, value, *args, **kwargs):
        self.queue.append(self._action_request("PUT", key, value))

    def Delete(self, key, *args, **kwargs):
        self.queue.append(self._action_request("DELETE", key))

    def Range(self, start=None, limit=None, *args, **kwargs):
        self.queue.append(self._action_request("RANGE", start, limit))

    def Slice(self, key_from=None, offset=None, *args, **kwargs):
        self.queue.append(self._action_request("SLICE", key_from, offset))

    def Batch(self, batch, *args, **kwargs):
        self.queue.append(self._action_request("BATCH", batch.container))

    def pop(self):
        return self.queue.pop()

    def clear(self):
        self.queue = []

    def execute(self, *args, **kwargs):
        datas = self.send(self.db_uid, 'PIPELINE', [self.queue, ], *args, **kwargs)
        self.clear()
        return datas