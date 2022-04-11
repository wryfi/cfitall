"""
The manager module implements a ProviderManager, which manages configuration
providers for a ConfigurationRegistry.
"""

import logging
from typing import Union, Optional, List

from cfitall.providers.base import ConfigProviderBase

logger = logging.getLogger(__name__)


class ProviderManager:
    #: list determining the order in which providers are merged
    ordering: List[str]

    def __init__(self, providers: Optional[List[ConfigProviderBase]] = None) -> None:
        """
        The ProviderManager manages configuration providers, handling registration,
        deregistration and ordering. It is attached to a registry's
        ``providers`` attribute.

        :param providers: optional list of preconfigured providers to manage
        """
        self.ordering: List[str] = []
        if not providers:
            providers = []
        for provider in providers:
            self.register(provider)

    def __repr__(self) -> str:
        return str(self.ordering)

    def get(self, name: str) -> Union[ConfigProviderBase, None]:
        """
        Retrieves a reference to the named provider from the manager.

        :param name: friendly name of a registered provider
        :return: provider instance or None
        """
        try:
            return getattr(self, name)
        except AttributeError:
            return None

    def register(self, provider: ConfigProviderBase) -> None:
        """
        Registers a provider with the manager.

        :param provider: an instance of a configured provider
        """
        if not hasattr(self, provider.provider_name):
            setattr(self, provider.provider_name, provider)
            self.ordering.append(provider.provider_name)
        else:
            logger.error(
                f"there is already a provider named {provider.provider_name} registered!"
            )

    def deregister(self, provider_name: str) -> None:
        """
        Deregisters a provider from the manager

        :param provider_name:
        """
        if hasattr(self, provider_name):
            delattr(self, provider_name)
        self.ordering = [prov for prov in self.ordering if prov != provider_name]

    def update_all(self) -> None:
        """
        Triggers each registered provider to run its update() function, updating
        the values it will return.
        """
        for provider_name in self.ordering:
            try:
                provider: Optional[ConfigProviderBase] = self.get(provider_name)
                if provider and not provider.update():
                    logger.error(f"provider {provider} failed to update!")
            except AttributeError:
                logger.error(f"could not find provider {provider_name}")
