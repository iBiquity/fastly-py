import asyncio
import os

from fastly.errors import *
from .auth import *
from .connection import Connection
from .models import *


class API(object):
    def __init__(self, host=os.environ.get('FASTLY_HOST', 'api.fastly.com'),
                 secure=os.environ.get('FASTLY_SECURE', True), port=None,
                 root='', timeout=5.0, key=None, session=None, loop=None):
        self.conn = Connection(host, secure, port, root, timeout,
                               session=session, loop=loop)

        if key:
            self.authenticate_by_key(key)

    def authenticate_by_key(self, key):
        self.conn.authenticator = KeyAuthenticator(key)

    async def authenticate_by_password(self, login, password):
        self.conn.authenticator = await create_session_authenticator(
            self.conn, login, password)

    def deauthenticate(self):
        self.conn.authenticator = None

    def service(self, id):
        return Service.find(self.conn, id=id)

    def version(self, service_id, version):
        return Version.find(self.conn, service_id=service_id, number=version)

    def domain(self, service_id, version, name):
        return Domain.find(self.conn, service_id=service_id, version=version,
                           name=name)

    def backend(self, service_id, version, name):
        return Backend.find(self.conn, service_id=service_id, version=version,
                            name=name)

    def settings(self, service_id, version):
        return Settings.find(self.conn, service_id=service_id, version=version)

    def condition(self, service_id, version, name):
        return Condition.find(self.conn, service_id=service_id,
                              version=version, name=name)

    def header(self, service_id, version, name):
        return Header.find(self.conn, service_id=service_id, version=version,
                           name=name)

    async def purge_url(self, host, path, soft=False):
        headers = {'Host': host}
        if soft:
            headers['Fastly-Soft-Purge'] = '1'

        resp, data = await self.conn.request('PURGE', path, headers=headers)
        return resp.status == 200

    async def soft_purge_url(self, host, path):
        return await self.purge_url(host, path, True)

    async def purge_service(self, service, soft=False):
        headers = {}
        if soft:
            headers['Fastly-Soft-Purge'] = '1'

        resp, data = await self.conn.request('POST',
                                             '/service/%s/purge_all' % service,
                                             headers=headers)
        return resp.status == 200

    async def soft_purge_service(self, service):
        return await self.purge_service(service, True)

    async def purge_key(self, service, key, soft=False):
        if type(self.conn.authenticator) is not KeyAuthenticator:
            raise AuthenticationError("This request requires an API key")

        headers = {}
        if soft:
            headers['Fastly-Soft-Purge'] = '1'

        resp, data = await self.conn.request('POST', '/service/%s/purge/%s' % (
            service, key), headers=headers)
        return resp.status == 200

    async def soft_purge_key(self, service, key):
        return await self.purge_key(service, key, True)

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __enter__(self):
        # warning use async with instead
        return self
