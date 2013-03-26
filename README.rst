===========
Py-elevator
===========

*py-elevator* is a python client for `Elevator <http://github.com/oleiade/Elevator>`_, a Key-Value store written in Python and based on levelDB, allows high performance on-disk bulk read/write.

Allows async, multithreaded and/or remote access to a multi-leveldb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and platforms.

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/py-elevator&title=Py-elevator&language=&tags=github&category=software

Requirements
============

- zmq-3.X
- leveldb
- pyzmq (built with zmq-3.X)
- plyvel


Debian repository
-----------------

The ``deb.oleiade.com`` debian repository exposes ``libzmq3``, ``libzmq3-dev``, ``libleveldb1`` and ``libleveldb1-dev`` packages in order to ease your dependencies management. Just add the following line to your ``/etc/apt/sources.list``:

.. code-block:: bash

    deb http://deb.oleiade.com/debian oneiric main



Installation
============

Just::

    pip install py-elevator


Usage
=====

**Nota** : See `Elevator <http://oleiade.github.com/Elevator>`_ documentation for details about server usage and implementation

Databases workaround
--------------------

.. code-block:: python

  >>> from pyelevator import Elevator

  # Elevator server holds a default db
  # which the client will automatically
  # connect to
  >>> E = Elevator()
  >>> E.db_name
  'default'

  # You can list remote databases
  >>> E.listdb()
  ['default', ]

  # Create a db
  >>> E.createdb('testdb')
  >>> E.listdb()
  ['default', 'testdb', ]

  # And bind your client to that new Db.
  >>> E.connect('testdb')

  # Note that you canno't connect to a db that doesn't exist yet
  >>> E.connect('dbthatdoesntexist')
  DatabaseError : "Database does not exist"

  # Sometimes, leveldb just messes up with the backend
  # When you're done with a db, you can drop it. Note that all it's files
  # will be droped too.
  >>> E.repairdb()
  >>> E.dropdb('testdb')


  # You can even register a pre-existing leveldb db
  # as an Elevator db. By creating it using it's path.
  >>> E.createdb('/path/to/my/existing/leveldb')
  >>> E.listdb()
  ['default', '/path/to/my/existing/leveldb', ]


  # Elevator objects can also spawn WriteBatches objects,
  # inheriting it's parent Elevator object configuration.
  >>> batch = E.WriteBatch()


Interact with a database:
-------------------------

.. code-block:: python

  >>> from pyelevator import Elevator
  >>> E = Elevator()                   # N.B : connected to 'default'

  >>> E.Put('abc', '123')
  >>> E.Put('easy as', 'do re mi')
  >>> E.Get('abc')
  '123'
  >>> E.MGet(['abc', 'easy as', 'you and me'])
  ['123', 'do re mi', None]
  >>> E.Delete('abc')
  >>> for i in xrange(10):
  ...     E.Put(str(i), str(i))

  # Range supports key_from, key_to params
  >>> E.Range('1', '9')
  [['1','1'],
   ['2','2'],
   ['3', '3'],
   ['4', '4'],
   ['5', '5'],
   ['6', '6'],
   ['7', '7'],
   ['8', '8'],
   ['9', '9'],
  ]

  # Or key_from, limit params
  >>> E.Slice('1', 2)
  [['1', '1'],
   ['2', '2'],
  ]

  # When RangeIter only knows about key_from/key_to for py-leveldb api
  # compatibility reasons
  >>> it = E.RangeIter('1', '2')
  >>> list(it)
  [['1', '1'],
   ['2', '2'],
  ]

  # Elevator objects supports with_statement too
  >>> with Elevator('testdb') as e:
  >>> ....e.Get('1')
  >>>
  '1'

Batches
-------

They're very handy and very fast when it comes to write a lot of datas to the database.
See LevelDB documentation for more informations. Use it through the WriteBatch client module class.
It has three base methods modeled on LevelDB's Put, Delete, Write.

.. code-block:: python

  >>> from pyelevator import WriteBatch, Elevator

  # Just like Elevator object, WriteBatch connects to 'default' as a default
  # But as it supports the exact same options that Elevator, you can
  # Init it with a pre-existing db
  >>> batch = WriteBatch()
  >>> batch = WriteBatch('testdb')

  >>> batch.Put('a', 'a')
  >>> batch.Put('b', 'b')
  >>> batch.Put('c', 'c')
  >>> batch.Delete('c')
  >>> batch.Write()

  >>> E = Elevator()
  >>> E.Get('a')
  'a'
  >>> E.Get('b')
  'b'
  >>> E.Get('c')
  KeyError: "Key not found"

  # Batches objects supports with_statement too
  # Write will be automatically called on __exit__
  >>> with WriteBatch('testdb') as batch:
  >>> ....batch.Put('abc', '123')
  >>> ....batch.Put('or simple as...', 'do re mi')
  >>>


*Code is clean and simple, don't hesitate to dig into it if you need more details about it's usage*
