from __future__ import absolute_import

from collections import deque

from .base import Client


class Pipeline(Client):
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)
        self.queue = []

    def _action_request(self, command, arguments):
        return {
            'COMMAND': command,
            'ARGS': arguments,
        }

    def add(self, command, arguments):
        self.queue.append(self._action_request(command, arguments))

    def pop(self):
        self.queue.pop()

    def clear(self):
        self.queue = []

    def push(self, *args, **kwargs):
        datas = self.send(self.db_uid, 'PIPELINE', list(self.queue), *args, **kwargs)
        self.queue = []
        return datas