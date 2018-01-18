"""
"""

from copy import copy
from string import Template


class Model(object):
    def __init__(self):
        self._original_attrs = None
        self.attrs = {}

    @classmethod
    async def query(cls, conn, pattern, method, suffix='', body=None,
                    **kwargs):
        url = Template(pattern).substitute(**kwargs)
        url += suffix

        headers = {'Content-Accept': 'application/json'}
        if method == 'POST' or method == 'PUT':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return await conn.request(method, url, body, headers)

    async def _query(self, method, suffix='', body=None):
        return await self.__class__.query(self.conn, self.INSTANCE_PATTERN,
                                          method, suffix, body, **self.attrs)

    async def _collection_query(self, method, suffix='', body=None):
        return await self.__class__.query(self.conn, self.COLLECTION_PATTERN,
                                          method, suffix, body, **self.attrs)

    async def save(self):
        if self._original_attrs:
            out = {}
            for k in self.attrs:
                if self.attrs[k] != self._original_attrs[k]:
                    out[k] = self.attrs[k]
            resp, data = await self._query('PUT', body=self.attrs)

        else:
            resp, data = await self._collection_query('POST', body=self.attrs)

        self._original_attrs = data
        self.attrs = data

    @classmethod
    async def find(cls, conn, **kwargs):
        resp, data = await cls.query(conn, cls.INSTANCE_PATTERN, 'GET',
                                     **kwargs)
        obj = cls.construct_instance(data)
        obj.conn = conn
        return obj

    @classmethod
    def construct_instance(cls, data):
        obj = cls()
        obj._original_attrs = data
        obj.attrs = copy(data)
        return obj


class Service(Model):
    COLLECTION_PATTERN = '/service'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$id'

    async def purge_key(self, key):
        await self._query('POST', '/purge/%s' % key)

    async def purge_all(self):
        await self._query('POST', '/purge_all')


class Version(Model):
    COLLECTION_PATTERN = Service.COLLECTION_PATTERN + '/$service_id/version'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$number'

    def check_backends(self):
        resp, data = self._query('GET', '/backend/check_all')
        return data


class Domain(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/domain'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'

    async def check_cname(self):
        resp, data = await self._query('GET', '/check')
        return (data[1], data[2])


class Backend(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/backend'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class Director(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/director'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class Origin(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/origin'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class Healthcheck(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/healthcheck'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class Syslog(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/syslog'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class User(Model):
    COLLECTION_PATTERN = '/user/$id'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$id'


class Settings(Model):
    INSTANCE_PATTERN = Version.COLLECTION_PATTERN + '/$version/settings'
    COLLECTION_PATTERN = INSTANCE_PATTERN


class Condition(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/condition'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'


class Header(Model):
    COLLECTION_PATTERN = Version.COLLECTION_PATTERN + '/$version/header'
    INSTANCE_PATTERN = COLLECTION_PATTERN + '/$name'
