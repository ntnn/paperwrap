paperwork python API wrapper and client
=======================================

| |Build Status|
| `paperwork <https://github.com/twostairs/paperwork>`__ is 'an open
source note-taking and archiving tool'.

| Supported: python 2.7, 3.3+
| Tests can be run with ``./run_tests.py``.

PyPI entry: `paperworks <https://pypi.python.org/pypi/paperworks/>`__

| ``wrapper.py`` is the actual api-wrapper.
| ``models.py`` contains classes for paperwork-instances, noteboooks,
notes and tags.
| ``paperwork.py`` is a command-line client.

CLI
===

``paperwork`` searches for the file ``~/.paperworkrc`` and, if found,
reads host, username and password - if the file is not found the client
prompts for values. A template can be found in the file
``paperworkrc.template``.

.. |Build Status| image:: https://travis-ci.org/ntnn/paperwork.py.svg?branch=master
   :target: https://travis-ci.org/ntnn/paperwork.py
