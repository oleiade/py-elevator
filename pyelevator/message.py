import msgpack
import logging

from .constants import FAILURE_STATUS, WARNING_STATUS


class MessageFormatError(Exception):
    pass


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        content = {
            'DB_UID': kwargs.pop('db_uid'),
            'COMMAND': kwargs.pop('command'),
            'ARGS': kwargs.pop('args'),
        }

        return msgpack.packb(content)


class Response(object):
    def __init__(self, raw_message):
        self.error = None
        errors_logger = logging.getLogger("errors_logger")
        message = msgpack.unpackb(raw_message)

        try:
            self.status = message.pop('STATUS')
            self._datas = message.pop('DATAS')
        except KeyError:
            errors_logger.exception("Invalid response message : %s" %
                                    message)
            raise MessageFormatError("Invalid response message")

        self._handle_failures()

    @property
    def datas(self):
        if hasattr(self, '_datas') and self._datas is not None:
            if (len(self._datas) == 1):
                return self._datas[0]
            return self._datas

    def _handle_failures(self):
        if self.status in (FAILURE_STATUS, WARNING_STATUS):
            self.error = {
                'code': int(self.datas[0]),
                'msg': self.datas[1],
            }

            if self.status == WARNING_STATUS:
                self._datas = self.datas[2:]
