"""
The manager module implements a ProviderManager, which manages configuration
providers for a ConfigurationRegistry.
"""

import logging
from typing import Union, Optional, Sequence

from cfitall.providers.base import ConfigProviderBase

logger = logging.getLogger(__name__)


class ProviderManager:
    def __init__(
        self, providers: Optional[Sequence[ConfigProviderBase]] = None
    ) -> None:
        """
        The ProviderManager manages configuration providers, handling registration,
        deregistration and ordering.

        :param providers: optional list of preconfigured providers to manage
        """
        self.ordering: Sequence[str] = []
        if not providers:
            providers = []
        for provider in providers:
            self.register(provider)

    def __repr__(self) -> str:
        return str(self.ordering)

    def get(self, name: str) -> Union[ConfigProviderBase, None]:
        try:
            return getattr(self, name)
        except AttributeError:
            return None

    def register(self, provider: ConfigProviderBase) -> None:
        if not hasattr(self, provider.provider_name):
            setattr(self, provider.provider_name, provider)
            self.ordering.append(provider.provider_name)
        else:
            logger.error(
                f"there is already a provider named {provider.provider_name} registered!"
            )

    def deregister(self, provider_name: str) -> None:
        if hasattr(self, provider_name):
            delattr(self, provider_name)
        self.ordering = [prov for prov in self.ordering if prov != provider_name]

    def update_all(self) -> None:
        for provider_name in self.ordering:
            try:
                provider: Optional[ConfigProviderBase] = self.get(provider_name)
                if provider and not provider.update():
                    logger.error(f"provider {provider} failed to update!")
            except AttributeError:
                logger.error(f"could not find provider {provider_name}")