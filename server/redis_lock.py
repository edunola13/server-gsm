# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from redlock import RedLock


class RedisLockFail(Exception):
    def __init__(self, message):
        super().__init__(message)


class Lock():
    def __init__(self, key, ttl=1000, retry=None, delay=None):
        self.key = key
        self.ttl = ttl
        retry = retry if retry else settings.REDIS_BLOCKER_RETRY
        delay = delay if delay else settings.REDIS_BLOCKER_DELAY
        print (delay)
        self.redis = RedLock(key, settings.REDIS_BLOCKER, retry, delay, ttl)

    def __enter__(self):
        if not self.redis.acquire():
            raise RedisLockFail("Can't get block")

    def __exit__(self, type, value, traceback):
        self.redis.release()
