import unittest2
import leveldb
import os
import time
import shutil
import uuid

from nose.tools import raises

from pyelevator import Elevator, WriteBatch
from pyelevator.constants import *
from pyelevator.error import *

from .fakers import TestDaemon


class ElevatorTest(unittest2.TestCase):
    def setUp(self):
        self.elevator_daemon = TestDaemon()
        self.elevator_daemon.start()
        self.client = Elevator(port=self.elevator_daemon.port)
        self._bootstrap_db()

    def tearDown(self):
        self.elevator_daemon.stop()
        del self.elevator_daemon
        del self.client

    def _bootstrap_db(self):
        batch = WriteBatch(port=self.elevator_daemon.port)

        for x in xrange(10):
            batch.Put(str(x), str(x))

        batch.Write()

    def test_connect_store_existing_db(self):
        self.client.connect('default')

        self.assertIsNotNone(self.client.db_name)
        self.assertIsNotNone(self.client.db_uid)
        self.assertIsInstance(self.client.db_uid, str)

    @raises(DatabaseError)
    def test_connect_to_store_non_existing_db(self):
        self.client.connect('dadahouse')

    def test_createdb_fs_existing_db(self):
        tmp_fs_db = os.path.join("/tmp", str(uuid.uuid4()))
        db = leveldb.LevelDB(tmp_fs_db)
        db.Put('abc', '123')
        db.Put('easy as', 'do re mi')
        del db

        self.client.createdb(tmp_fs_db)
        self.assertIn(tmp_fs_db, self.client.listdb())

        self.client.connect(tmp_fs_db)
        self.assertEqual(self.client.Get('abc'), '123')
        self.assertEqual(self.client.Get('easy as'), 'do re mi')

        shutil.rmtree(tmp_fs_db)

    def test_createdb_fs_non_db(self):
        tmp_fs_db = os.path.join("/tmp", str(uuid.uuid4()))
        self.client.createdb(tmp_fs_db)
        self.assertIn(tmp_fs_db, self.client.listdb())

        self.client.connect(tmp_fs_db)
        self.client.Put('abc', '123')
        self.client.Put('easy as', 'do re mi')

        self.elevator_daemon.stop()
        time.sleep(2)

        db = leveldb.LevelDB(tmp_fs_db)
        self.assertEqual(db.Get('abc'), '123')
        self.assertEqual(db.Get('easy as'), 'do re mi')

        shutil.rmtree(tmp_fs_db)

    def test_get_with_existing_key(self):
        value = self.client.Get('1')

        self.assertIsInstance(value, str)  # No error (tuple) returned
        self.assertEqual(value, '1')

    @raises(KeyError)
    def test_get_with_invalid_key(self):
        self.client.Get('abc')

    def test_mget_with_valid_keys(self):
        values = self.client.MGet(['1', '2', '3'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('1', '2', '3'))

    def test_mget_with_invalid_keys(self):
        values = self.client.MGet(['1', 'abc', '3'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('1', None, '3'))

    def test_mget_with_one_existing_key(self):
        values = self.client.MGet(['1'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('1', ))

    def test_mget_with_one_non_existing_key(self):
        values = self.client.MGet(['touptoupidou'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, (None, ))

    def test_put_valid_value(self):
        self.client.Put('abc', '123')

        res = self.client.Get('abc')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '123')

    @raises(TypeError)
    def test_put_invalid_value(self):
        self.client.Put('abc', 123)

    def test_delete_existing_key(self):
        self.client.Put('abc', '123')
        self.client.Delete('abc', '123')

    def test_range_of_len_ten(self):
        res = self.client.Range('0', '9')

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 10)

        for r in res:
            self.assertIsNotNone(r)
            self.assertIsInstance(r, tuple)
            self.assertEqual(r[0], r[1])

    def test_range_of_len_one(self):
        res = self.client.Range('1', '1')

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)

        content = res[0]
        self.assertIsInstance(content, tuple)
        self.assertEqual(content, ('1', '1'))

    def test_slice_of_len_ten(self):
        res = self.client.Slice('0', 9)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 9)

    def test_slice_of_len_one(self):
        res = self.client.Slice('1', 1)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)

        content = res[0]
        self.assertIsInstance(content, tuple)
        self.assertEqual(content, ('1', '1'))
