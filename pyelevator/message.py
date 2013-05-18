# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import msgpack
import logging
import lz4


errors_logger = logging.getLogger("errors_logger")


class MessageFormatError(Exception):
    pass


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        try:
            content = [
                kwargs.get('db_uid'),  # uid can eventually be None
                kwargs.pop('command'),
            ]
            content.extend(kwargs.pop('args'))  # Keep the request message flat
        except KeyError:
            raise MessageFormatError("Invalid request format : %s" % str(kwargs))

        return msgpack.packb(content)


class Response(object):
    def __init__(self, raw_message, *args, **kwargs):
        message = msgpack.unpackb(raw_message)

        try:
            self.status = message[0]
            self.err_code = message[1]
            self.err_msg = message[2]
            self.data = message[3:]
        except IndexError:
            errors_logger.exception("Invalid response message: {}"
                                    .format(message))
            MessageFormatError("Invalid response message")
