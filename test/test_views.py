import unittest
from flask import Flask
import flask_testing


class TestRoutes(flask_testing.TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_do_feed(self):
        response = self.client.get('/recent')
        print (response.headers)
        self.assertIn('rsspy', response)

if __name__ == '__main__':
    unittest.main()