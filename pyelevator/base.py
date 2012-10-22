from __future__ import absolute_import

import zmq

from .constants import FAILURE_STATUS
from .message import Request, Response, ResponseHeader
from .error import ELEVATOR_ERROR, TimeoutError
from .utils.snippets import sec_to_ms, ms_to_sec


class Client(object):
    def __init__(self, db=None, *args, **kwargs):
        self.protocol = kwargs.pop('protocol', 'tcp')
        self._timeout = sec_to_ms(kwargs.pop('timeout', 1))
        self.endpoint = kwargs.pop('endpoint', '127.0.0.1:4141')

        self._db_uid = None
        self.host = "%s://%s" % (self.protocol, self.endpoint)

        db = 'default' if db is None else db
        self._connect(db=db)

    def __del__(self):
        self._close()

    def _connect(self, db):
        self.context = zmq.Context()
        self.poller = zmq.Poller()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.poller.register(self.socket, zmq.POLLIN)
        self.socket.connect(self.host)
        self.connect(db)

    def _close(self):
        self.socket.close()
        self.context.term()

    @property
    def timeout(self):
        if not hasattr(self, '_timeout'):
            self._timeout = sec_to_ms(1)
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        value_in_ms = sec_to_ms(value)
        self._timeout = value_in_ms
        self.socket.setsockopt(zmq.RCVTIMEO, self._timeout)

    def connect(self, db_name, *args, **kwargs):
        datas = self.send(None, 'DBCONNECT', [db_name], *args, **kwargs)
        self.db_uid = datas[0]
        self.db_name = db_name
        return

    def mount(self, db_name, *args, **kwargs):
        self.send(None, 'DBMOUNT', [db_name], *args, **kwargs)
        return

    def unmount(self, db_name, *args, **kwargs):
        self.send(None, 'DBUMOUNT', [db_name], *args, **kwargs)
        return

    def listdb(self, *args, **kwargs):
        return self.send(self.db_uid, 'DBLIST', {}, *args, **kwargs)

    def createdb(self, key, db_options=None, *args, **kwargs):
        db_options = db_options or {}
        self.send(self.db_uid, 'DBCREATE', [key, db_options], *args, **kwargs)
        return

    def dropdb(self, key, *args, **kwargs):
        return self.send(self.db_uid, 'DBDROP', [key], *args, **kwargs)

    def repairdb(self, *args, **kwargs):
        self.send(self.db_uid, 'DBREPAIR', {}, *args, **kwargs)
        return

    def send(self, db_uid, command, arguments, *args, **kwargs):
        orig_timeout = ms_to_sec(self.timeout)  # Store updates is made from seconds
        timeout = kwargs.pop('timeout', 0)
        compression = kwargs.pop('compression', False)

        # If a specific timeout value was provided
        # store the old value, and update current timeout
        if timeout > 0:
            self.timeout = timeout

        self.socket.send_multipart([Request(db_uid=db_uid,
                                            command=command,
                                            args=arguments,
                                            meta={'compression': compression})],)

        try:
            raw_header, raw_response = self.socket.recv_multipart()
            header = ResponseHeader(raw_header)
            response = Response(raw_response, compression=compression)

            if header.status == FAILURE_STATUS:
                raise ELEVATOR_ERROR[header.err_code](header.err_msg)
        except zmq.core.error.ZMQError:
            # Restore original timeout and raise
            self.timeout = orig_timeout
            raise TimeoutError("Timeout : Server did not respond in time")

        # Restore original timeout
        self.timeout = orig_timeout

        return response.datas
