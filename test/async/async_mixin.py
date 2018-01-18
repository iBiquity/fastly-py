import asyncio
import os
import unittest

import fastly
from fastly.async.fastly import API
from fastly.errors import AuthenticationError


def async_test(f):
    """Decorator that runs a test using run_until_complete.  """

    def wrapper(self, *args, **kw):
        coro = asyncio.coroutine(f)
        asyncio.set_event_loop(None)
        self.loop.run_until_complete(coro(self, *args, **kw))

    return wrapper


class AsyncMixin(object):
    loop = asyncio.get_event_loop()

    @async_test
    async def test_purge(self):
        self.assertTrue(await self.api.purge_url(self.host, '/'))

    @unittest.skipIf(os.environ.get('FASTLY_API_KEY') is None,
                     "Default API Key is not authorized to run this test")
    @async_test
    async def test_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        self.assertTrue(await self.api.purge_key(self.service_id, 'foo'))

    @async_test
    async def test_cookie_purge_by_key(self):
        self.api.deauthenticate()
        await self.api.authenticate_by_password(self.user, self.password)
        with self.assertRaises(fastly.AuthenticationError):
            await self.api.purge_key(self.service_id, 'foo')

    @async_test
    async def test_soft_purge(self):
        self.api.deauthenticate()
        self.assertTrue(await self.api.soft_purge_url(self.host, '/'))

    @unittest.skipIf(os.environ.get('FASTLY_API_KEY') is None,
                     "Default API Key is not authorized to run this test")
    @async_test
    async def test_soft_purge_by_key(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        self.assertTrue(await self.api.soft_purge_key(self.service_id, 'foo'))

    @async_test
    async def test_cookie_soft_purge_by_key(self):
        self.api.deauthenticate()
        await self.api.authenticate_by_password(self.user, self.password)
        with self.assertRaises(AuthenticationError):
            await self.api.soft_purge_key(self.service_id, 'foo')

    @async_test
    async def test_auth_error(self):
        self.api.deauthenticate()
        with self.assertRaises(AuthenticationError):
            await self.api.conn.request('GET', '/current_customer')

    @async_test
    async def test_auth_key_success(self):
        self.api.deauthenticate()
        self.api.authenticate_by_key(self.api_key)
        await self.api.conn.request('GET', '/current_customer')

    @async_test
    async def test_auth_session_success(self):
        self.api.deauthenticate()
        await self.api.authenticate_by_password(self.user, self.password)
        await self.api.conn.request('GET', '/current_customer')
