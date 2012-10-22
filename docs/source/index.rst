:orphan:
Welcome to py-elevator's documentation!
=======================================

py-elevator is a python client for `Elevator <http://github.com/oleiade/Elevator>`_, in Python and based on levelDB allowing high performance on-disk bulk read/write. Which provides async, multithreaded and/or remote access to a multi-leveldb backend.
It Relies on the zeromq network library and msgpack serialization format as a messaging protocol.
It was made with portability, stability, and focus on performance in mind.

.. _requirements:

Requirements
------------

.. code-block:: bash

    pyzmq (built against zmq-3.X)
    msgpack-python

.. _installation:
Installation
------------

To install the last stable version (master)

.. code-block:: bash

    $ git clone git@github.com/oleiade/py-elevator
    $ cd py-elevator
    $ python setup.py install

To install the last tag with pip

.. code-block:: bash

    pip install -e git+git@github.com/oleiade/py-elevator@{{tag-name}}.git#egg=py-elevator