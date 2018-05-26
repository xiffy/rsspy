import unittest
import sys
from rsspy import do_feed, home

class TestRoutes(unittest.TestCase):
    print (sys.path)
    def test_do_feed(self):
        self.assertIn('rsspy', home())

if __name__ == '__main__':
    unittest.main()