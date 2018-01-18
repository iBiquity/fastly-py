import unittest
import os
import fastly
from fastly.fastly import API


class APITest(unittest.TestCase):

    def setUp(self):
        self.api = API()
        self.host = os.environ.get('FASTLY_SERVICE_HOST', 'test.com')
        self.service_id = os.environ.get('FASTLY_SERVICE_ID', 'test.com')
        self.api_key = os.environ.get('FASTLY_API_KEY', 'TESTAPIKEY')
        self.user = os.environ.get('FASTLY_USER', 'foo@example.com')
        self.password = os.environ.get('FASTLY_PASSWORD', 'password')

    def tearDown(self):
        self.api.close()

    def test_purge(self):
        self.assertTrue(self.api.purge_url(self.host, '/'))

    @unittest.skipIf(os.environ.get('FASTLY_API_KEY') == None,
                     "Default API Key is not authorized to run this test")
    def test_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        self.assertTrue(self.api.purge_key(self.service_id, 'foo'))

    def test_cookie_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_password(self.user, self.password)
        with self.assertRaises(fastly.AuthenticationError):
            self.api.purge_key(self.service_id, 'foo')

    def test_soft_purge(self):
        self.api.deauthenticate()
        self.assertTrue(self.api.soft_purge_url(self.host, '/'))

    @unittest.skipIf(os.environ.get('FASTLY_API_KEY') == None,
                     "Default API Key is not authorized to run this test")
    def test_soft_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        self.assertTrue(self.api.soft_purge_key(self.service_id, 'foo'))

    def test_cookie_soft_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_password(self.user, self.password)
        with self.assertRaises(fastly.AuthenticationError):
            self.api.soft_purge_key(self.service_id, 'foo')

    def test_auth_error(self):
        self.api.deauthenticate()
        with self.assertRaises(fastly.AuthenticationError):
            self.api.conn.request('GET', '/current_customer')

    def test_auth_key_success(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        self.api.conn.request('GET', '/current_customer')

    def test_auth_session_success(self):
        self.api.deauthenticate()
        self.api.authenticate_by_password(self.user, self.password)
        self.api.conn.request('GET', '/current_customer')

    def test_sets_default_user_agent_header(self):
        default_headers = self.api.conn.default_headers
        self.assertEqual(default_headers['User-Agent'],
                         'fastly-py-v{}'.format(fastly._version.__version__))

if __name__ == '__main__':
    unittest.main()