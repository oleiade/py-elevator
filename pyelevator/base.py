from __future__ import absolute_import

import zmq
import msgpack

from .message import Request, Response
from .error import ELEVATOR_ERROR

from elevator.constants import FAILURE_STATUS

from elevator.db import DatabaseOptions


class Client(object):
    def __init__(self, db=None, *args, **kwargs):
        self.protocol = kwargs.pop('protocol', 'tcp')
        self.bind = kwargs.pop('bind', '127.0.0.1')
        self.port = kwargs.pop('port', '4141')
        self._db_uid = None
        self.host = "%s://%s:%s" % (self.protocol, self.bind, self.port)

        db = 'default' if db is None else db
        self._connect(db=db)

    def __del__(self):
        self._close()

    def _connect(self, db):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)
        self.connect(db)

    def _close(self):
        self.socket.close()
        self.context.term()

    def connect(self, db_name):
        self.db_uid = self.send(db_name, 'DBCONNECT', [db_name])
        self.db_name = db_name
        return

    def listdb(self):
        return self.send(self.db_uid, 'DBLIST', {})

    def createdb(self, key, db_options=None):
        db_options = db_options if not None else DatabaseOptions()
        return self.send(self.db_uid, 'DBCREATE', [key, db_options])

    def dropdb(self, key):
        return self.send(self.db_uid, 'DBDROP', [key])

    def repairdb(self):
        return self.send(self.db_uid, 'DBREPAIR', {})

    def send(self, db_uid, command, args):
        self.socket.send_multipart([Request(db_uid=db_uid, command=command, args=args)])
        response = Response(self.socket.recv_multipart()[0])

        if response.error is not None:
            raise ELEVATOR_ERROR[response.error['code']](response.error['msg'])
        return response.datas
