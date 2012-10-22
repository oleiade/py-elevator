import unittest2

from pyelevator import Elevator, WriteBatch
from pyelevator.constants import *

from .fakers import TestDaemon


class WriteBatchElevator(unittest2.TestCase):
    def setUp(self):
        self.elevator_daemon = TestDaemon()
        self.elevator_daemon.start()
        self.endpoint = '{0}:{1}'.format(self.elevator_daemon.bind, self.elevator_daemon.port)
        self.client = Elevator(endpoint=self.endpoint)
        self.batch = WriteBatch(endpoint=self.endpoint)

    def tearDown(self):
        self.elevator_daemon.stop()
        del self.elevator_daemon
        del self.client
        del self.batch

    def _bootstrap_db(self):
        for l in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
            self.batch.Put(l, l)
        self.batch.Write()

    def test_batch_put_only(self):
        for x in xrange(10):
            self.batch.Put(str(x), str(x))

        self.assertEqual(len(self.batch.container), 10)
        for elem in self.batch.container:
            self.assertEqual(elem[0], SIGNAL_BATCH_PUT)
            self.assertIsInstance(elem[1], str)

        self.batch.Write()

        for x in xrange(10):
            r = self.client.Get(str(x))
            self.assertIsNotNone(r)
            self.assertIsInstance(r, str)
            self.assertEqual(r, str(x))

        def test_batch_mixed_put_delete(self):
            self.batch.Delete('a')
            self.batch.Put('a')
            self.batch.Delete('b')

            self.batch.Write()

            self.assertEqual(self.client.Get('a'), 'a')
            self.assertIsNone(self.client.Get('b'))

        def test_batch_with(self):
            with self.batch as batch:
                for x in xrange(10):
                    batch.Put(str(x), str(x))

                self.assertEqual(len(batch.container), 10)
                for elem in batch.container:
                    self.assertEqual(elem[0], SIGNAL_BATCH_PUT)
                    self.assertIsInstance(elem[1], str)

            for x in xrange(10):
                r = self.client.Get(str(x))
                self.assertIsNotNone(r)
                self.assertIsInstance(r, str)
                self.assertEqual(r, str(x))
