import unittest2
import msgpack

from nose.tools import raises

from pyelevator.message import Request, Response, ResponseHeader,\
                               MessageFormatError


class RequestTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @raises(MessageFormatError)
    def test_request_with_missing_mandatory_arg(self):
        Request(**{
            'meta': {},
            'db_uid': '123-456-789',
                'args': [],
        })

    def test_request_with_all_args(self):
        try:
            Request(**{
                'meta': {},
                'db_uid': '123-456-789',
                'command': 'GET',
                'args': [],
            })
        except MessageFormatError:
            self.fail("Request() raised MessageFormatError unexpectedly!")

    def test_request_without_db_uid_arg(self):
        try:
            req = Request(**{
                'meta': {},
                'command': 'GET',
                'args': [],
            })
        except MessageFormatError:
            self.fail("Request() raised MessageFormatError unexpectedly!")

        unpacked_req = msgpack.unpackb(req)
        self.assertIsNone(unpacked_req['uid'])

    @raises(MessageFormatError)
    def test_response_header_with_missing_mandatory_arg(self):
        raw_header = msgpack.packb({
            'status': -1,
            'err_code': 0,
        })
        ResponseHeader(raw_header)

    def test_response_header_with_all_args(self):
        try:
            raw_header = msgpack.packb({
                'status': -1,
                'err_code': 0,
                'err_msg': ""
            })
            resp = ResponseHeader(raw_header)
        except MessageFormatError:
            self.fail("ResponseHeader() raised MessageFormatError unexpectedly!")

        self.assertTrue(hasattr(resp, 'status'))
        self.assertTrue(hasattr(resp, 'err_code'))
        self.assertTrue(hasattr(resp, 'err_msg'))

    @raises(MessageFormatError)
    def test_response_with_missing_mandatory_arg(self):
        raw_resp = msgpack.packb({})
        ResponseHeader(raw_resp)
