# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import zmq

from .constants import FAILURE_STATUS
from .message import Request, Response, ResponseHeader
from .error import ELEVATOR_ERROR, TimeoutError
from .utils.snippets import sec_to_ms, ms_to_sec
from .utils.patterns import enum


class Client(object):
    STATUSES = enum('ONLINE', 'OFFLINE')

    def __init__(self, db_name=None, *args, **kwargs):
        self.transport = kwargs.pop('transport', 'tcp')
        self.endpoint = kwargs.pop('endpoint', '127.0.0.1:4141')
        self.host = "%s://%s" % (self.transport, self.endpoint)

        self.context = None
        self.socket = None

        self._timeout = sec_to_ms(kwargs.pop('timeout', 1))
        self._status = self.STATUSES.OFFLINE
        self._db_uid = None

        self.setup_socket()

        if kwargs.pop('auto_connect', True) is True:
            self.connect(db_name)

    def __del__(self):
        self.teardown_socket()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status in [self.STATUSES.ONLINE, self.STATUSES.OFFLINE]:
            self._status = status
        else:
            raise TypeError("Provided status should be a Pipeline.STATUSES")

    def setup_socket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect(self.host)

    def teardown_socket(self):
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

    def connect(self, db_name=None, *args, **kwargs):
        if self.status == self.STATUSES.OFFLINE:
            self.status = self.STATUSES.ONLINE

        db_name = 'default' if db_name is None else db_name
        self.db_uid = self.send(None, 'DBCONNECT', [db_name], *args, **kwargs)[0]
        self.db_name = db_name
        return

    def disconnect(self, *args, **kwargs):
        self.status == self.STATUSES.OFFLINE
        self.teardown_socket()

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
        except zmq.ZMQError:
            # Restore original timeout and raise
            self.timeout = orig_timeout
            raise TimeoutError("Timeout : Server did not respond in time")

        # Restore original timeout
        self.timeout = orig_timeout

        return response.datas
