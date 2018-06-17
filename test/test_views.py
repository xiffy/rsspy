import unittest
from flask import Flask
from rsspy.rsspy import create_rsspy
import rsspy


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

if __name__ == '__main__':
    unittest.main()