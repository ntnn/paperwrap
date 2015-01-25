#!/usr/bin/env python

import sys, unittest
if sys.version_info[:2][0] == 2:
    from pip import main as pip
    pip(['install', '3to2', 'mock', '--upgrade', '--user'])
    from lib3to2 import main as three2two
    three2two.main('lib3to2.fixes', '-n --no-diffs -w test'.split(' '))

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('./test/')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
