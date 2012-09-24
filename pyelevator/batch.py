from __future__ import absolute_import

from .constants import SIGNAL_BATCH_PUT, SIGNAL_BATCH_DELETE
from .base import Client


class WriteBatch(Client):
    def __init__(self, *args, **kwargs):
        self.container = []
        super(WriteBatch, self).__init__(*args, **kwargs)

    def Put(self, key, value):
        self.container.append([SIGNAL_BATCH_PUT, key, value])

    def Delete(self, key):
        self.container.append([SIGNAL_BATCH_DELETE, key])

    def Write(self):
        self.send(self.db_uid, 'BATCH', [self.container])
        self.container = []
        return
