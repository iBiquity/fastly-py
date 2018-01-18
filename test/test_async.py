import os
import sys
import unittest

import fastly

# this is to allow for a graceful skip from python 2.7
if sys.version_info[0] == 3:
    from async.async_mixin import AsyncMixin, API
else:
    AsyncMixin = object


@unittest.skipIf(sys.version_info[0] == 2, "Async is only for python 3")
class AsyncTest(unittest.TestCase, AsyncMixin):
    def setUp(self):
        self.api = API(loop=self.loop)
        self.host = os.environ.get('FASTLY_SERVICE_HOST', 'test.com')
        self.service_id = os.environ.get('FASTLY_SERVICE_ID', 'test.com')
        self.api_key = os.environ.get('FASTLY_API_KEY', 'TESTAPIKEY')
        self.user = os.environ.get('FASTLY_USER', 'foo@example.com')
        self.password = os.environ.get('FASTLY_PASSWORD', 'password')

    def tearDown(self):
        self.loop.run_until_complete(self.api.conn.close())

    def test_sets_default_user_agent_header(self):
        default_headers = self.api.conn.default_headers
        self.assertEqual(default_headers['User-Agent'],
                         'fastly-py-v{}'.format(fastly._version.__version__))


if __name__ == '__main__':
    unittest.main()
