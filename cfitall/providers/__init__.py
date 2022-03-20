class ConfigProviderBase(object):
    @property
    def dict(self):
        raise NotImplementedError
