#!/usr/bin/env python

import collections
import logging
import pickle
import uuid

import rod.connection as connection
import rod.errors as errors

logger = logging.getLogger('rod.model')


# From https://github.com/SPSCommerce/redlock-py
unlock_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end"""

Lock = collections.namedtuple("Lock", ("resource_name", "lock_id"))


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

    def lock(self, ttl):
        resource_name = 'lock:{key}'.format(prefix=self.prefix, key=self._redis_key)
        logger.debug('Trying to acquire %s', resource_name)
        lock_id = str(uuid.uuid4())

        try:
            # nx = True prevents setting value if it's already set
            # px is expire flag in ms
            lock_acquired = connection.common.set(resource_name, lock_id, nx=True, px=ttl)
        except Exception:
            logger.exception('Failed to acquire lock')
            return False

        if lock_acquired:
            logger.debug('Acquired lock')
            self.lock = Lock(resource_name, lock_id)
            return self.lock
        else:
            logger.debug('Resource was already locked')
            return False



    def unlock(self):
        try:
            lock = self.lock
        except AttributeError:
            # If lock doesn't exists we don't have anything to unlock
            return

        if lock:
            try:
                connection.common.eval(unlock_script, 1, self.lock.resource_name, self.lock.lock_id)
            except Exception:
                return

    @property
    def _redis_key(self):
        return '{prefix}:{key}'.format(prefix=self.prefix, key=getattr(self, self.key))

    def save(self):
        if not connection.common:
            raise errors.ConnectionNotSetup()
        # dump only "public" attributes from current instance
        public_attributes = {name: value for name, value in vars(self).items() if not name.startswith('_')}
        connection.common.set(self._redis_key, pickle.dumps(public_attributes))
