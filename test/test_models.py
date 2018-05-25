import unittest
from model import feed
from model import bookmark

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

    def test_get_all(self):
        f = feed.Feed()
        self.assertGreater(len(f.get_all()), 2)

class TestBookmark(unittest.TestCase):
    def test_init(self):
        b = bookmark.Bookmark()
        self.assertEqual(b.ID, None)

    def test_gat_bookamrks(self):
        b = bookmark.Bookmark()
        self.assertGreater(len(b.get_bookmarks(1)), 2)

if __name__ == '__main__':
    unittest.main()