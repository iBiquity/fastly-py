"""
"""
import sys

from .errors import assert_response_status
if sys.version_info[0] < 3:
    from urllib import urlencode
else:
    from urllib.parse import urlencode


class KeyAuthenticator(object):
    def __init__(self, key):
        self.key = key

    def add_auth(self, headers):
        headers['Fastly-Key'] = self.key

class SessionAuthenticator(object):
    def __init__(self, conn, login, password):
        body = urlencode({ 'user': login, 'password': password })
        resp, data = conn.request('POST', '/login', body)
        assert_response_status(resp.status, data)
        self.session_key = resp.getheader('Set-Cookie')
        assert self.session_key is not None, "Failed to set cookie"

    def add_auth(self, headers):
        headers['Cookie'] = self.session_key
