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
        self.redis = RedLock(key, settings.REDIS_BLOCKER, retry, delay, ttl)

    def __enter__(self):
        self.redis.acquire()

    def __exit__(self, type, value, traceback):
        self.redis.release()

    # def __enter__(self):
    #     self.lock = self.redis.lock(self.key, self.ttl)
    #     if self.lock is False:
    #         raise RedisLockFail("Can't get block")
    #     return self.lock

    # def __exit__(self, type, value, traceback):
    #     if self.lock:
    #         self.redis.unlock(self.lock)
