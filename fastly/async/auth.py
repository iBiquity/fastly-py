"""
"""

from fastly.errors import assert_response_status


class KeyAuthenticator(object):
    def __init__(self, key):
        self.key = key

    def add_auth(self, headers):
        headers['Fastly-Key'] = self.key


class SessionAuthenticator(object):
    def add_auth(self, headers):
        headers['Cookie'] = self.session_key

    async def setup_session_key(self, conn, login, password):
        body = {'user': login, 'password': password}
        resp, data = await conn.request('POST', '/login', body)
        assert_response_status(resp.status, data)

        self.session_key = resp.headers.get('Set-Cookie')
        assert self.session_key is not None, "Failed to set cookie"


async def create_session_authenticator(conn, login, password):
    ret = SessionAuthenticator()
    await ret.setup_session_key(conn, login, password)
    return ret
