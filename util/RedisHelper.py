# -*- coding: utf-8 -*-
import redis
from ApiConfiger import ApiConfig

class RedisHelper(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            conf = ApiConfig()
            cls.instance = super(RedisHelper, cls).__new__(cls)
            cls.redis = redis.Redis(host=conf.get("redis", "host"), port=conf.getint("redis", "port"))
        return cls.instance

    def __init__(self, *args, **kwargs):
        pass

    def getRedis(self):
        return self.redis
