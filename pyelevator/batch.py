from __future__ import absolute_import

from .constants import SIGNAL_BATCH_PUT, SIGNAL_BATCH_DELETE
from .base import Client
from .utils.snippets import sec_to_ms


class WriteBatch(Client):
    def __init__(self, *args, **kwargs):
        # Remove intentionaly timeout from kwargs
        # in order to let Client timeout act normally
        # for connexion
        timeout = sec_to_ms(kwargs.pop('timeout', 10))
        super(WriteBatch, self).__init__(*args, **kwargs)
        # Force batches to have their own timeout
        self._timeout = timeout
        self.container = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.Write()

    def Put(self, key, value):
        self.container.append([SIGNAL_BATCH_PUT, key, value])

    def Delete(self, key):
        self.container.append([SIGNAL_BATCH_DELETE, key])

    def Write(self, *args, **kwargs):
        self.send(self.db_uid, 'BATCH', [self.container], *args, **kwargs)
        self.container = []
        return
