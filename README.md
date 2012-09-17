# Overview

*py-elevator* is a python client for [Elevator](http://github.com/oleiade/Elevator), a minimalistic database engine written in Python and based on levelDB.
Allows async, multithreaded and/or remote acces to a multidb backend.
Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and platforms.

# Usage

*See [Elevator](http://oleiade.github.com/Elevator) documentation for details about server usage and implementation*

### Databases workaround

```python
>>> from pyelevator import Elevator
>>> E = Elevator()                 # Elevator server holds a default db
>>> E.db_name                      # which the client will automatically
'default'                          # connect to

>>> E.listdb()                     # You can list remote databases
['default', ]

>>> E.createdb('testdb')           # Create a db
>>> E.listdb()
['default', 'testdb', ]
>>> E.connect('testdb')            # And bind your client to that new Db.
>>> E.connect('dbthatdoesntexist') # Note that you canno't connect to a db that doesn't exist yet
KeyError : "Database does not exist"
>>> E.repairdb()                   # Sometimes, leveldb just messes up with the backend
>>> E.dropdb('testdb')             # When you're done with a db, you can drop it. Note that all it's files
                                   # will be droped too.
                                   
# You can even register a pre-existing leveldb db
# as an Elevator db. By creating it using it's path.
>>> E.createdb('/path/to/my/existing/leveldb')
>>> E.listdb()
['default', '/path/to/my/existing/leveldb', ]
```

### Interact with a database:

```python
>>> from pyelevator import Elevator
>>> E = Elevator()             # N.B : connected to 'default'
>>> E.Put('abc', 'cba')
>>> E.Get('abc')
'cba'
>>> E.Delete('abc')
>>> for i in xrange(10):
...     E.Put(str(i), str(i))
>>> E.Range('1', '9')          # Range supports key_from, key_to params
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
>>> E.Range('1', 2)            # Or key_from, limit params
[['1', '1'],
 ['2', '2'],
]
>>> it = E.RangeIter('1', '2') # When RangeIter only knows about key_from/key_to for py-leveldb api
>>> list(it)                   # compatibility reasons
[['1', '1'],
 ['2', '2'],
]
```

### Batches 

They're very handy and very fast when it comes to write a lot of datas to the database.
See LevelDB documentation for more informations. Use it through the WriteBatch client module class.
It has three base methods modeled on LevelDB's Put, Delete, Write.

```python
>>> from pyelevator import WriteBatch, Elevator
>>> batch = WriteBatch()          # Just like Elevator object, WriteBatch connects to 'default' as a default
>>> batch = WriteBatch('testdb')  # But as it supports the exact same options that Elevator, you can
>>> batch.Put('a', 'a')           # Init it with a pre-existing db
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
```

# Api

## Elevator object

### Methods

* **Get(key)**, fetches a specific key in connected db

* **Put(key, value)**, inserts key/value pair in connected db

* **Delete(key)**, deletes the specified key in connected db

* **Range(start=None, limit=None)**, returns a whole lot of data following the specified key range, note that limit can whether be a key to stop to, or an offset.

* **RangeIter(start=None, limit=None)**, idem, but returns an iterator

* **connect(db_name)**, connects the current Elevator instance to a database

* **listdb()**, lists server databases

* **createdb(db_name)**, creates a database

* **dropdb(db_name)**, drops an existing database

* **repairdb()**, repairs currently connected database

## WriteBatch object

### Methods

* **Put(key, value)**, stack a command to insert a key/value pair in WriteBatch instance

* **Delete(key)**, stack a command to delete the key in WriteBatch

* **Write()**, applies the WriteBatch server-side