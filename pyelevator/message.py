import msgpack
import logging


errors_logger = logging.getLogger("errors_logger")


class MessageFormatError(Exception):
    pass


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        content = {
            'meta': {},
            'uid': kwargs.pop('db_uid'),
            'cmd': kwargs.pop('command'),
            'args': kwargs.pop('args'),
        }

        return msgpack.packb(content)


class Response(object):
    def __init__(self, raw_message):
        message = msgpack.unpackb(raw_message)

        try:
            self.meta = message['meta']
            self.datas = message['datas']
        except KeyError:
            errors_logger.exception("Invalid response message : %s" %
                                    message)
            raise MessageFormatError("Invalid response message")
