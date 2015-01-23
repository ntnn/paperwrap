from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))
package_name = 'paperworks'

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, package_name, 'wrapper.py')) as f:
    version = re.search("__version__ = '([^']+)'", f.read()).group(1)

setup(
    name = package_name,
    version = version,

    description = 'API Wrapper for the open-source note taking tool paperwork',
    long_description = long_description,

    url = 'https://github.com/ntnn/paperwork.py',

    author = 'Nelo Wallus',
    author_email = 'wallus.nelo@gmail.com',

    license = 'MIT',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords = 'paperwork rocks twostairs api wrapper',

    packages = find_packages(exclude = [ 'tests*' ])
)

