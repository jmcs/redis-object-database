import logging

import redis

common = None   # common redis connection

logger = logging.getLogger('rod.connection')


def setup(redis_host='localhost', port=6379):
    global common, lock_manager
    logger.debug('Connecting to %s:%s', redis_host, port)
    common = redis.StrictRedis(host=redis_host, port=port, db=0)
