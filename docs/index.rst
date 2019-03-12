==========
Blockchain
==========

This is the documentation of **Blockchain**.


How does this Blockchain implementation work?
=============================================

**Short Disclaimer:**
It is just a private ``Python 3.7.2`` project. Its purposes is to get a little bit familiar with the Python projects and the concepts of Blockchains.
Therefore it is not intended for production usage, and any warranties are excluded.


This implementation produces a simple ``CLI`` and a ``Miner``. It is necessary to get up and running a local Miner.
The CLI then uses the Miners ``REST`` interface to interact with it.
Created ``messages`` get synchronized with all other known Miners (``neighbours``) in the Blockchain network.
A Miner asks all its neighbours periodically (if not max amount of neighbours is reached) to send unknown Miner and connects to them.
Also in a periodical manner, Miner synchronizes their local Blockchain with the chains of there neighbours and use the longest valid chain in the network.


Proof of Work
=============

A very simple implementation of a ``Proof of Work`` algorithm.
The ``SHA-256`` hash value of the concatenation of the previous ``proof`` and the ``proof`` of the new Block has to start with ``difficulty`` trailing 0s.


Miner Implementation
====================

**This Miner implementation offers a REST API with the following endpoints:**

- ``/add`` (PUT): needs the URL parameter ``message``. Adds the message to the local cache of unprocessed data.
    - ``response`` (200): JSON with message: 'Message added!'
    - ``response`` (400): JSON with message: 'No Message added!'

- ``/chain`` (GET): Returns the miners local chain.
    - ``response`` (200): JSON with the actual chain and its length.

- ``neighbours`` (GET): Returns the miners neighbours.
    - ``response`` (200): JSON with the actual neighbours and its length.

- ``data`` (GET): Returns the miners local cache of unprocessed data.
    - ``response`` (200): JSON with the actual list of unprocessed data.

|

**The miner uses a set of files for normal operation:**

- ``<filename>.chain``: Representation of the actual file.
- ``<filename>.hash``: ``SHA-156`` of the actual chain file. Is used to check if the local chain differs from its on disc representation.
- ``<filename>_<date>_<time>``: Older versions of the chain file. Created at ``<date>_<time>``.

|

**The Miner runs several Threads and a Process to run parallel and periodical tasks:**

- ``Gossip Job`` (Thread): Implementation of a simple ``Gossip Protocol``. Fetches periodical all ``neighbours`` of its ``neighbours``.
- ``Sync Chain Job`` (Thread): To get the actual longest global chain. Fetches periodical the chain of all ``neighbours``.
- ``Sync Unprocessed Data Job`` (Thread): To propagate unprocessed data through the network. Fetches periodical the set of unprocessed data of all ``neighbours``.
- ``Backup Local Chain Job`` (Thread): To backup the local chain to disc. Backups periodical the local chain to disc if they differ from each other.
- ``Server Process`` (Process): Servers the Miners REST API in a separate process.
- ``Communication Job`` (Thread): Communication thread to exchange message with the server process.


Improvements
============

- Miner endpoint (health) to check availability and provide opportunity to delete a neighbour.


Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
