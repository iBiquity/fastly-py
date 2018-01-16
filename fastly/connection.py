"""
"""
import sys
if sys.version_info[0] < 3:
    from httplib import HTTPSConnection, HTTPConnection
else:
    from http.client import HTTPSConnection, HTTPConnection
import json
from ._version import __version__
from .errors import assert_response_status


class Connection(object):
    def __init__(self, host='api.fastly.com', secure=True, port=None, root='',
                 timeout=10.0):
        self.host = host
        self.secure = secure
        self.port = port
        self.root = root
        self.timeout = timeout

        self.authenticator = None
        self.http_conn = None
        self.default_headers = { 'User-Agent': 'fastly-py-v{}'.format(__version__) }

    def request(self, method, path, body=None, headers=None):
        headers = headers if headers is not None else {}
        headers.update(self.default_headers)

        if not self.port:
            self.port = 443 if self.secure else 80

        connection = HTTPSConnection if self.secure else HTTPConnection
        if not isinstance(self.http_conn, connection):
            self.close()
            self.http_conn = connection(self.host, self.port,
                                        timeout=self.timeout)

        if self.authenticator:
            self.authenticator.add_auth(headers)

        self.http_conn.request(method, self.root + path, body, headers=headers)
        response = self.http_conn.getresponse()
        body = response.read()
        try:
            data = json.loads(body)
        except ValueError:
            data = body

        assert_response_status(response.status, body)
        return (response, data)

    def close(self):
        if self.http_conn:
            self.http_conn.close()
