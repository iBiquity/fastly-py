"""
"""
import asyncio
import json

import aiohttp
from aiohttp.client import _RequestContextManager

from fastly._version import __version__
from fastly.errors import assert_response_status


class Connection(object):
    def __init__(self, host='api.fastly.com', secure=True, port=None, root='',
                 timeout=10.0, session=None, loop=None):
        self.host = host
        self.secure = secure
        self.port = port
        self.timeout = timeout
        self.root = root

        self.authenticator = None
        self.http_conn = None
        self.default_headers = {
            'User-Agent': 'fastly-py-v{}'.format(__version__)}
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self._close_session = session is None
        self.session = session if session is not None else \
            aiohttp.ClientSession(loop=loop)

    async def request(self, method, path, body=None, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        if not self.port:
            self.port = 443 if self.secure else 80

        if not self.root:
            self.root = '{http}://{host}:{port}'.format(
                http='https' if self.secure else 'http',
                host=self.host, port=self.port)

        if self.authenticator:
            self.authenticator.add_auth(headers)

        # needed for the custom method "PURGE"
        async with _RequestContextManager(
                self.session._request(method=method,
                                      url=self.root + path,
                                      data=body,
                                      headers=headers)) as response:
            body = await response.read()

        try:
            data = json.loads(body)
        except ValueError:
            data = body

        assert_response_status(response.status, body)

        return (response, data)

    async def close(self):
        if self._close_session:
            await self.session.close()

    @asyncio.coroutine
    def __aenter__(self):
        return self

    @asyncio.coroutine
    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        # warning use async with instead
        return self
