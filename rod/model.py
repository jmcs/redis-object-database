#!/usr/bin/env python

import logging

import yaml

import rod.connection as connection
import rod.errors as errors

logger = logging.getLogger('rod.model')


class Model(object):
    prefix = ''
    key = ''
    search_properties = []

    def __contains__(self, item):
        match = False
        search_properties = self.search_properties or vars(self)
        for attribute in search_properties:
            value = getattr(self, attribute)
            try:
                match += item.lower() in value.lower()
            except TypeError:
                pass
        return match

    def __str__(self):
        return yaml.dump(vars(self))

    @classmethod
    def all(cls):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        logger.debug('Getting all %s', cls.prefix)
        keys = connection.common.keys(cls.prefix+':*')
        raw_values = connection.common.mget(keys) if keys else []
        values = [cls(**yaml.load(v.decode())) for v in raw_values]
        return values

    @classmethod
    def get(cls, uid):

        if not connection.common:
            raise errors.ConnectionNotSetup()
        key = '{prefix}:{key}'.format(prefix=cls.prefix, key=uid)
        json_value = connection.common.get(key)
        if not json_value:
            raise KeyError
        values = yaml.load(json_value.decode())
        return cls(**values)

    def delete(self):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        connection.common.delete(self.redis_key)

    @property
    def _redis_key(self):
        return '{prefix}:{key}'.format(prefix=self.prefix, key=getattr(self, self.key))

    def save(self):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        connection.common.set(self._redis_key, str(self))