class ConfigProviderBase(object):
    # each provider must implement a unique provider_name
    provider_name: str = "not_implemented"

    @property
    def dict(self) -> dict:
        """
        The dict property should return a dictionary of the configuration values
        obtained by the provider. This dict is then combined and reconciled with
        that of the other providers to produce the final configuration.
        """
        raise NotImplementedError

    def update(self) -> bool:
        """
        The update() method signals the provider to read/update its internal data
        and should return True on successful update or False on failure.
        """
        raise NotImplementedError
