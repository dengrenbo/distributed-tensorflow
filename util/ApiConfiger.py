import ConfigParser
import os


class ApiConfig(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApiConfig, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        path = os.path.split(os.path.realpath(__file__))[0] + '/../conf/config'
        self.config.read(path)

    def get(self, *args):
        return self.config.get(*args)

    def getint(self, *args):
        return self.config.getint(*args)

    def getfloat(self, *args):
        return self.config.getfloat(*args)

    def getboolean(self, *args):
        return self.config.getboolean(*args)
