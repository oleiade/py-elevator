import unittest2
import plyvel
import os
import time
import shutil
import uuid

from types import GeneratorType

from nose.tools import raises

from pyelevator import Elevator, WriteBatch
from pyelevator.constants import *
from pyelevator.error import *

from .fakers import TestDaemon


class ElevatorTest(unittest2.TestCase):
    def setUp(self):
        self.elevator_daemon = TestDaemon()
        self.elevator_daemon.start()
        self.endpoint = '{0}:{1}'.format(self.elevator_daemon.bind, self.elevator_daemon.port)
        self.client = Elevator(endpoint=self.endpoint)
        self._bootstrap_db()

    def tearDown(self):
        self.elevator_daemon.stop()
        del self.elevator_daemon
        del self.client

    def _bootstrap_db(self):
        batch = WriteBatch(endpoint=self.endpoint)

        for x in xrange(10):
            batch.Put(str(x), str(x + 10))

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
        db = plyvel.DB(tmp_fs_db, create_if_missing=True)
        db.put('abc', '123')
        db.put('easy as', 'do re mi')
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

        db = plyvel.DB(tmp_fs_db, create_if_missing=True)
        self.assertEqual(db.get('abc'), '123')
        self.assertEqual(db.get('easy as'), 'do re mi')

        shutil.rmtree(tmp_fs_db)

    def test_get_with_existing_key(self):
        value = self.client.Get('1')

        self.assertIsInstance(value, str)  # No error (tuple) returned
        self.assertEqual(value, '11')

    @raises(KeyError)
    def test_get_with_invalid_key(self):
        self.client.Get('abc')

    def test_mget_with_valid_keys(self):
        values = self.client.MGet(['1', '2', '3'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('11', '12', '13'))

    def test_mget_with_invalid_keys(self):
        values = self.client.MGet(['1', 'abc', '3'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('11', None, '13'))

    def test_mget_with_one_existing_key(self):
        values = self.client.MGet(['1'])

        self.assertIsInstance(values, tuple)
        self.assertEqual(values, ('11', ))

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
            # boostraped values are from 10 to 19
            self.assertEqual(int(r[1]), int(r[0]) + 10)

    def test_range_of_len_ten_without_keys(self):
        res = self.client.Range('0', '9', include_key=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 10)

        for r in res:
            self.assertIsNotNone(r)
            # boostraped values are from 10 to 19
            self.assertGreaterEqual(int(r), 10)
            self.assertLessEqual(int(r), 19)

    def test_range_of_len_ten_without_values(self):
        res = self.client.Range('0', '9', include_value=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 10)

        for r in res:
            self.assertIsNotNone(r)
            self.assertGreaterEqual(int(r), 0)
            self.assertLessEqual(int(r), 9)

    def test_range_of_len_one(self):
        res = self.client.Range('1', '1')

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)

        content = res[0]
        self.assertIsInstance(content, tuple)
        self.assertEqual(content, ('1', '11'))

    def test_range_of_len_one_without_keys(self):
        res = self.client.Range('1', '1', include_key=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)
        self.assertEqual(res, ('11',))

    def test_range_of_len_one_without_values(self):
        res = self.client.Range('1', '1', include_value=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)
        self.assertEqual(res, ('1',))

    def test_slice_of_len_ten(self):
        res = self.client.Slice('0', 9)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 9)

        for r in res:
            self.assertIsNotNone(r)
            self.assertIsInstance(r, tuple)
            # boostraped values are from 10 to 19
            self.assertEqual(int(r[1]), int(r[0]) + 10)

    def test_slice_of_len_ten_without_keys(self):
        res = self.client.Slice('0', 9, include_key=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 9)

        for r in res:
            self.assertIsNotNone(r)
            self.assertGreaterEqual(int(r), 0)
            # boostraped values are from 10 to 19
            self.assertLessEqual(int(r), 19)

    def test_slice_of_len_ten_without_values(self):
        res = self.client.Slice('0', 9, include_value=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 9)

        for r in res:
            self.assertIsNotNone(r)
            self.assertGreaterEqual(int(r), 0)
            self.assertLessEqual(int(r), 9)

    def test_slice_of_len_one(self):
        res = self.client.Slice('1', 1)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)

        content = res[0]
        self.assertIsInstance(content, tuple)
        self.assertEqual(content, ('1', '11'))

    def test_slice_of_len_one_without_keys(self):
        res = self.client.Slice('1', 1, include_key=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)
        self.assertEqual(res, ('11',))

    def test_slice_of_len_one_without_values(self):
        res = self.client.Slice('1', 1, include_value=False)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 1)
        self.assertEqual(res, ('1',))

    def test_rangeiter_of_len_ten(self):
        it = self.client.RangeIter(key_from='0', key_to='9')

        content = list(it)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 10)

        for elem in content:
            self.assertIsInstance(elem, tuple)
            self.assertEqual(len(elem), 2)

    def test_rangeiter_of_len_one(self):
        it = self.client.RangeIter(key_from='1', key_to='1')

        content = list(it)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 1)

        datas = content[0]
        self.assertIsInstance(datas, tuple)
        self.assertEqual(len(datas), 2)

    def test_spawn_writebatch_from_elevator(self):
        batch = self.client.WriteBatch()

        self.assertIsInstance(batch, WriteBatch)
        self.assertEqual(batch.endpoint, self.client.endpoint)
        self.assertEqual(batch.protocol, self.client.protocol)
        self.assertEqual(batch.db_uid, self.client.db_uid)
        self.assertEqual(batch.db_name, self.client.db_name)
        self.assertTrue(batch.status == WriteBatch.STATUSES.ONLINE)
