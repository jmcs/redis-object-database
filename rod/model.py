#!/usr/bin/env python

import logging
import pickle

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
            except (TypeError, AttributeError):
                pass
        return match

    @classmethod
    def all(cls):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        logger.debug('Getting all %s', cls.prefix)
        keys = connection.common.keys(cls.prefix+':*')
        raw_values = connection.common.mget(keys) if keys else []
        values = [cls(**pickle.loads(v)) for v in raw_values]
        return values

    @classmethod
    def get(cls, uid):

        if not connection.common:
            raise errors.ConnectionNotSetup()
        key = '{prefix}:{key}'.format(prefix=cls.prefix, key=uid)
        pickled = connection.common.get(key)
        if not pickled:
            raise KeyError
        values = pickle.loads(pickled)
        return cls(**values)

    def delete(self):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        connection.common.delete(self._redis_key)

    @property
    def _redis_key(self):
        return '{prefix}:{key}'.format(prefix=self.prefix, key=getattr(self, self.key))

    def save(self):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        # dump only "public" attributes from current instance
        public_attributes = {name: value for name, value in vars(self).items() if not name.startswith('_')}
        connection.common.set(self._redis_key, pickle.dumps(public_attributes))
