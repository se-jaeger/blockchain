==========
Blockchain
==========

This is the documentation of **Blockchain**.


How does this Blockchain implementation work?
=============================================

**Short Disclaimer:**
It is just a private ``Python 3.7.2`` project. Its purposes is to get a little bit familiar with the Python projects and the concepts of Blockchains.
Therefore it is not intended for production usage and any warranties are excluded.


This implementation produces a simple ``CLI`` and a ``Miner``. It is necessary to get up and running a local Miner.
The CLI then uses the Miners ``REST`` interface to interact with it.
Created ``messages`` get synchronized with all other known Miners (``neighbours``) in the Blockchain network.
A Miner asks periodically all its neighbours (if not max amount of neighbours is reached) to send unknown Miner and connects to them.
Also in a periodical manner, Miner synchronize their local Blockchain with the chains of there neighbours and just use the longest valid chain in the network.


Proof of Work
=============

Very simple implementation of a ``Proof of Work`` algorithm.
The ``SHA-256`` hash value of the concatenation of the previous ``proof`` and the ``proof`` of the new Block has to start with ``difficulty`` trailing 0s.


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
