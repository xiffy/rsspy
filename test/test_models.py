import unittest
from model import feed
from model import bookmark
from model import entry
from model import user
from model import group
from model import group_feed



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

    def test_bookmarked(self):
        b = bookmark.Bookmark()
        self.assertIsNone(b.bookmarked(userID=1, entryID=1))
        self.assertFalse(b.bookmarked(userID=None, entryID=1))
        self.assertFalse(b.bookmarked(userID=1, entryID=None))
        self.assertTrue(b.bookmarked(userID=1, entryID=20383))


class TestEntry(unittest.TestCase):

    def test_init(self):
        e = entry.Entry()
        self.assertEqual(e.ID, None)

    def test_init_with_id(self):
        e = entry.Entry(28160)
        self.assertEqual(e.title, 'Death to America')

    def test_fetch_by_feed(self):
        e = entry.Entry()
        rows = e.fetch_by_feed(2)
        self.assertGreater(len(rows), 3)

class TestGroup(unittest.TestCase):

    def test_init(self):
        g = group.Group()
        self.assertEqual(g.ID, None)

    def test_init_with_id(self):
        g = group.Group(1)
        self.assertEqual(g.description, 'Comics')

    def test_feeds(self):
        g = group.Group(2)
        self.assertGreater(len(g.feeds), 2)

class TestGroupFeed(unittest.TestCase):

    def test_init(self):
        g = group_feed.GroupFeed()
        self.assertEqual(g.ID, None)
        self.assertIsInstance(g, group_feed.GroupFeed)

    def test_get_feeds(self):
        g = group_feed.GroupFeed(1)
        self.assertEqual(g.ID, 1)
        self.assertGreater(len(g.get_feeds(groupID=1)), 2)

class TestUser(unittest.TestCase):

    def test_init(self):
        u = user.User()
        self.assertEqual(u.username, None)
        self.assertIsInstance(u, user.User)
        assert getattr(u, 'ID', 'Undefined') == 'Undefined'

    def test_be_someone(self):
        u = user.User(1)
        self.assertEqual(u.username, 'xiffy')
        self.assertGreater(len(u.bookmarks), 3)

if __name__ == '__main__':
    unittest.main()