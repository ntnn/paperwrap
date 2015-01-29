#Paperwork API Wrapper and Command Line Client  
[![Build Status](https://travis-ci.org/ntnn/paperwork.py.svg?branch=master)](https://travis-ci.org/ntnn/paperwork.py)  
[paperwork](https://github.com/twostairs/paperwork) is 'an open source note-taking and archiving tool'.

Supported: python 2.7, 3.3+  
Tests can be run with `./run_tests.py`.

PyPI entry: [paperworks](https://pypi.python.org/pypi/paperworks/) 

`wrapper.py` is the actual api-wrapper.  
`models.py` contains classes for paperwork-instances, noteboooks, notes and tags.  
`paperworks.py` is a command-line client.

#Command Line Interface  
`paperworks` connects to the remote host and provides a command line interface to manage the notes. 
If a file `.paperworkrc` in `$HOME` exists `paperworks` parses the credentials. If no such file exists the credentials can be entered via prompt.
`help` will display the vailable commands. 

