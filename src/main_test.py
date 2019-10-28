import unittest
import cache_test


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(cache_test)
    unittest.TextTestRunner(verbosity=2).run(suite)
