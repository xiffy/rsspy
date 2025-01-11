import unittest
from unittest import skip

from rsspy.model.feed import Feed
from rsspy.model.bookmark import Bookmark
from rsspy.model.entry import Entry
from rsspy.model.user import User
from rsspy.model.group import Group
from rsspy.model.group_feed import GroupFeed


class TestFeed(unittest.TestCase):
    def test_init(self):
        f = Feed()
        self.assertEqual(f.ID, None)

    def test_init_with_id(self):
        f = Feed(2)
        self.assertEqual(f.url, "https://www.nrc.nl/rss/")

    def test_with_entries(self):
        f = Feed(2)
        f.with_entries()
        self.assertGreater(len(f.entries), 2)

    def test_get_all(self):
        f = Feed()
        self.assertGreater(len(f.get_all()), 2)


class TestBookmark(unittest.TestCase):
    def test_init(self):
        b = Bookmark()
        self.assertEqual(b.ID, None)

    def test_gat_bookamrks(self):
        b = Bookmark()
        self.assertGreater(len(b.get_bookmarks(1)), 2)

    def test_bookmarked(self):
        b = Bookmark()
        self.assertIsNone(b.bookmarked(userID=1, entryID=1))
        self.assertFalse(b.bookmarked(userID=None, entryID=1))
        self.assertFalse(b.bookmarked(userID=1, entryID=None))
        # self.assertTrue(b.bookmarked(userID=1, entryID=20383))


class TestEntry(unittest.TestCase):
    def test_init(self):
        e = Entry()
        self.assertEqual(e.ID, None)

    @skip
    def test_init_with_id(self):
        e = Entry(28160)
        self.assertEqual(e.title, "Death to America")

    def test_fetch_by_feed(self):
        e = Entry()
        rows = e.fetch_by_feed(2)
        self.assertGreater(len(rows), 3)


class TestGroup(unittest.TestCase):
    def test_init(self):
        g = Group()
        self.assertEqual(g.ID, None)

    def test_init_with_id(self):
        g = Group(1)
        self.assertEqual(g.description, "Comics")

    def test_feeds(self):
        g = Group(1)
        self.assertGreater(len(g.feeds), 1)


class TestGroupFeed(unittest.TestCase):
    def test_init(self):
        g = GroupFeed()
        self.assertEqual(g.ID, None)
        self.assertIsInstance(g, GroupFeed)

    def test_get_feeds(self):
        g = GroupFeed(1)
        self.assertEqual(g.ID, 1)
        self.assertGreater(len(g.get_feeds(groupID=1)), 2)


class TestUser(unittest.TestCase):
    def test_init(self):
        u = User()
        self.assertEqual(u.username, None)
        self.assertIsInstance(u, User)
        assert getattr(u, "ID", "Undefined") == "Undefined"

    def test_be_someone(self):
        u = User(1)
        self.assertEqual(u.username, "xiffy")
        self.assertGreater(len(u.bookmarks), 3)


if __name__ == "__main__":
    unittest.main()
