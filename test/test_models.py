import unittest
from model import feed

class TestFeed(unittest.TestCase):
    def test_init(self):
        f = feed.Feed()
        self.assertEqual(f.ID, None)

    def test_init_with_id(self):
        f = feed.Feed(2)
        self.assertEqual(f.url, 'https://www.nrc.nl/rss/')

    def test_with_entries(self):
        f = feed.Feed(2)
        f.with_entries()
        self.assertGreater(len(f.entries), 2)


if __name__ == '__main__':
    unittest.main()