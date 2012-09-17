# Client

In order to communicate with elevator, a Python client is avalaible (more to come. Feel free to make your own, I'll be glad to merge it into the repo).

It exposes the Elevator object which api is quite similar to py-leveldb one. This similarity was kept in order to enhance the move from py-leveldb to Elevator in already existing projects. Note that by default, client to 'default' database. As Elevator implements a multi-db system, you can create/list/delete/repair databases. To connect to another database, use the eponyme function .connect()

Here is a demo:

```python
>>> from elevator.client import Elevator
>>> E = Elevator()  # N.B : connected to 'default'
>>> Ebis = Elevator('testdb')  # You can even construct your client with desired db to connect to
>>> E.connect('testdbbis')  # Or even rebind client to a new database
>>> E.Put('abc', 'cba')
>>> E.Get('abc')
'cba'
>>> E.Delete('abc')
>>> for i in xrange(10):
...     E.Put(str(i), str(i))
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
>>> E.Range('1', 2)
[['1', '1'],
 ['2', '2'],
]
>>> it = E.RangeIter('1', 2)
>>> list(it)
[['1', '1'],
 ['2', '2'],
]
```

Batches are implemented too. They're very handy and very fast when it comes to write a lot of datas to the database. See LevelDB documentation for more informations. Use it through the WriteBatch client module class. It has three base methods modeled on LevelDB's Put, Delete, Write.

Example:

```python
>>> from elevator.client import WriteBatch, Elevator
>>> batch = WriteBatch()  # N.B : port, host, and timeout options are available here
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
```

# Api

## Elevator object

### Methods

**Get(key)**, fetches a specific key in connected db
**Put(key, value)**, inserts key/value pair in connected db
**Delete(key)**, deletes the specified key in connected db
**Range(start=None, limit=None)**, returns a whole lot of data following the specified key range, note that limit can whether be a key to stop to, or an offset.
**RangeIter(start=None, limit=None)**, idem, but returns an iterator
**connect(db_name)**, connects the current Elevator instance to a database
**listdb()**, lists server databases
**createdb(db_name)**, creates a database

## WriteBatch object

### Methods

**Put(key, value)**, stack a command to insert a key/value pair in WriteBatch instance
**Delete(key)**, stack a command to delete the key in WriteBatch
**Write()**, applies the WriteBatch server-side