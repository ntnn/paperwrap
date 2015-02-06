from setuptools import setup, find_packages
from codecs import open
from os import path
import re
import sys

here = path.abspath(path.dirname(__file__))
package_name = 'paperworks'

with open(path.join(here, 'README.rst'), 'r', encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, package_name, 'wrapper.py'), 'r') as f:
    version = re.search("__version__ = u?'([^']+)'", f.read()).group(1)

if __name__ == "__main__":
    # part taken from https://github.com/gbin/err/blob/master/setup.py#L54-68
    if sys.version_info[0] < 3:
        try:
            from lib3to2 import main as three2two
        except ImportError:
            print('If this keeps happening please install'
                  '3to2 yourself with `pip install 3to2 --user`.')
            from pip import main as mainpip
            mainpip(['install', '3to2', 'mock', '--user'])
            from lib3to2 import main as three2two
        three2two.main('lib3to2.fixes',
                       '-n --no-diffs -w paperworks'.split(' '))

    setup(
        name=package_name,
        version=version,

        description='API Wrapper and command line client for'
                    'the open-source note taking tool paperwork',
        long_description=long_description,

        url='https://github.com/ntnn/paperwork.py',

        author='Nelo Wallus',
        author_email='wallus.nelo@gmail.com',

        license='MIT',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',

            'License :: OSI Approved :: MIT License',

            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        ],

        entry_points={
            'console_scripts': ['paperworks = paperworks.cli:main']
            },

        install_requires=[
            'PyYAML',
            'fuzzywuzzy',
            'python-Levenshtein',
            'requests'],

        keywords='paperwork rocks twostairs api wrapper',

        packages=find_packages(exclude=['test'])
    )
