import unittest
from flask import Flask

from rsspy.model import user

from rsspy.rsspy import create_rsspy


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app = create_rsspy()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_do_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_feed(self):
        response = self.app.get('/feed/2')
        self.assertEqual(response.status_code, 200)

    def test_feed_xml(self):
        response = self.app.get('/feed/2/xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-type'], 'text/xml; charset=utf-8')
        assert '<title>rsspy: home - NRC</title>'.encode('utf-8') in response.data

    def test_allfeeds(self):
        response = self.app.get('/allfeeds')
        self.assertEqual(response.status_code, 200)
        assert '<li><a href="/feed/1">xiffy</a></li>'.encode('utf-8') in response.data

    def test_recent(self):
        response = self.app.get('/recent')
        self.assertEqual(response.status_code, 200)
        assert '<div class="feed_grid">'.encode('utf-8') in response.data

    def test_user_recent(self):
        response = self.app.get('/user/recent')
        self.assertEqual(response.status_code, 200)
        assert '<div class="feed_grid">'.encode('utf-8') in response.data

    def test_bookmarks(self):
        response = self.app.get('/xiffy/bookmarks')
        self.assertEqual(response.status_code, 200)
        assert '<title>Bookmarks by:'.encode('utf-8') in response.data
        #print (response.data)

    def test_groupview(self):
        response = self.app.get('/group/1')
        self.assertEqual(response.status_code, 200)
        assert '<title>Grouped feeds: Comics'.encode('utf-8') in response.data

    def test_viewfeedlist(self):
        response = self.app.get('/widget/feedlist')
        self.assertEqual(response.status_code, 200)

    def test_userpage(self):
        u = user.User(1)
        with self.app as c:
            with c.session_transaction() as sess:
                sess['das_hash'] = u.das_hash
            response = c.get('/user')
            assert '<div class="grid_container">'.encode('utf-8') in response.data

if __name__ == '__main__':
    unittest.main()

    #app.add_url_rule('/settings/feed/<id>', view_func=maint_feed, methods=['GET', 'POST'])
    #app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
    #app.add_url_rule('/bookmark/<entryID>', view_func=bookmark, methods=['POST'])
    #app.add_url_rule('/bookmark/<bookmarkID>', view_func=remove_bookmark, methods=['DELETE'])
    #app.add_url_rule('/groupfeed/', view_func=groupfeed, methods=['POST'])
    #app.add_url_rule('/groupfeed/<groupID>/<feedID>', view_func=remove_groupfeed, methods=['DELETE'])
    #app.add_url_rule('/group/add', view_func=create_group, methods=['POST'])
    #app.add_url_rule('/group/delete', view_func=remove_group,  methods=['DELETE'])
    #app.add_url_rule('/feed/add', view_func=create_feed, methods=['POST'])
    #app.add_url_rule('/send_digest', view_func=send_digest,methods=['GET'])
