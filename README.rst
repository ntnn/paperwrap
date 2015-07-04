Paperwork API Wrapper and Command Line Client
=============================================

| |Build Status| |Scrutinizer Code Quality|
| `paperwork <https://github.com/twostairs/paperwork>`__ is 'an open
source note-taking and archiving tool'.

| Supported: python 2.7, 3.3+
| Tests can be run with ``./run_tests.py``.

PyPI entry: `paperwrap <https://pypi.python.org/pypi/paperwrap/>`__

| ``wrapper.py`` is the actual api-wrapper.
| ``models.py`` contains classes for paperwork-instances, notebooks,
notes and tags.
| ``paperwork.py`` is a command-line client with the entry-point
``paperwrap``.

Command Line Interface
======================

``paperwrap`` connects to the remote host and provides a command line
interface to manage the notes. The credentials are read with requests
from the ``.netrc`` file.

.. |Build Status| image:: https://travis-ci.org/ntnn/paperwrap.svg?branch=master
   :target: https://travis-ci.org/ntnn/paperwrap
.. |Scrutinizer Code Quality| image:: https://scrutinizer-ci.com/g/ntnn/paperwrap/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/ntnn/paperwrap/?branch=master
