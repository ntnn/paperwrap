
if __name__ == '__main__':
    import unittest
    testsuite = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
