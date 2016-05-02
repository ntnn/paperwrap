#Paperwork API Wrapper and Command Line Client
[![Build Status](https://travis-ci.org/ntnn/paperwrap.svg?branch=master)](https://travis-ci.org/ntnn/paperwrap)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ntnn/paperwrap/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ntnn/paperwrap/?branch=master)
[paperwork](https://github.com/twostairs/paperwork) is 'an open source note-taking and archiving tool'.

Supported: python 2.7, 3.3+
Tests can be run with `./run_tests.py`.

PyPI entry: [paperwrap](https://pypi.python.org/pypi/paperwrap/)

`wrapper.py` is the actual api-wrapper.
`models.py` contains classes for paperwork-instances, notebooks, notes and tags.
`paperwork.py` is a command-line client with the entry-point `paperwrap`.

#Command Line Interface
`paperwrap` connects to the remote host and provides a command line interface to manage the notes.
The credentials are read with requests from the `.netrc` file.

Mirrors:
* https://github.com/ntnn/paperwrap
* https://gitlab.com/ntnn/paperwrap
* https://bitbucket.org/ntnn/paperwrap
