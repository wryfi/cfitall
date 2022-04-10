"""
The registry module implements the ConfigurationRegistry, the core structure
and entry point for cfitall.
"""

from decimal import Decimal
import logging
import json
from typing import Union, Dict, Sequence, Optional
import os

import yaml

from cfitall import utils, ConfigValueType
from cfitall.manager import ProviderManager
from cfitall.providers.base import ConfigProviderBase
from cfitall.providers.environment import EnvironmentProvider
from cfitall.providers.filesystem import FilesystemProvider

logger = logging.getLogger(__name__)


class ConfigurationRegistry(object):
    def __init__(
        self,
        name: str,
        defaults: Dict = None,
        providers: Optional[Sequence[ConfigProviderBase]] = None,
    ) -> None:
        """
        The configuration registry holds configuration data from different sources
        and reconciles it for retrieval. If the defaults dict is provided, it
        will be used to seed the default configuration values for the registry,
        equivalent to calling set_default() for each configuration key in defaults.

        :param name: namespace for configuration registry
        :param defaults: default configuration values
        :param providers: providers to add to the registry
        """
        if not defaults:
            defaults = {}
        self.name = name
        self.values = {"super": {}, "defaults": defaults}
        if providers is not None:
            self.providers = ProviderManager(providers=providers)
        else:
            self.providers = ProviderManager()
            path = [os.path.join("/etc", name)]
            if home := os.getenv("HOME"):
                path.insert(0, os.path.join(home, ".local", "etc", name))
            self.providers.register(FilesystemProvider(path, name))
            self.providers.register(EnvironmentProvider(name))

    @property
    def all(self) -> Dict:
        """
        Returns a dictionary of all the configuration data that is considered
        for merging, before it is merged into the final configuration.
        """
        values = self.values.copy()
        for provider_name in self.providers.ordering:
            try:
                if provider := self.providers.get(provider_name):
                    values[provider.provider_name] = provider.dict
            except (KeyError, ValueError):
                logger.error(f"error reading values from provider {provider_name}")
        return values

    @property
    def config_keys(self) -> list[str]:
        """
        Returns a list of currently used configuration keys as dotted paths, for
        use with the get() or set() methods.
        """
        config_keys = [key for key, value in self.flattened.items()]
        return sorted(config_keys)

    @property
    def dict(self) -> Dict:
        """
        Returns a dict of merged configuration data
        """
        return self._merge_configs()

    @property
    def env_vars(self) -> list[str]:
        """
        Returns a list of environment variables known from config files and defaults
        """
        if env_provider := self.providers.get("environment"):
            keys = [key.upper() for key, value in self.flattened.items()]
            keys = [
                env_provider.prefix + key.replace(".", env_provider.level_separator)  # type: ignore
                for key in keys
            ]
            return sorted(keys)
        return []

    @property
    def flattened(self) -> Dict:
        """
        Returns a "flattened" dictionary of merged config values,
        condensing hierarchies into dotted paths and returning simple
        key-value pairs.
        """
        return utils.flatten_dict(self.dict)

    @property
    def json(self) -> str:
        """
        Returns json representation of merged configuration.
        """
        return json.dumps(self.dict, indent=4, sort_keys=True)

    @property
    def yaml(self) -> str:
        """
        Returns yaml representation of merged configuration.
        """
        return yaml.dump(self.dict)

    def get(self, config_key: str) -> Union[ConfigValueType, None]:
        """
        Get a configuration value by its dotted path key; returns the requested
        value as its native type stored in the registry.
        """
        try:
            return self.flattened[config_key]
        except (KeyError, TypeError):
            return None

    def get_bool(self, config_key: str) -> Union[bool, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as a boolean or raises TypeError.
        """
        try:
            return bool(self.flattened[config_key])
        except KeyError:
            return None

    def get_decimal(self, config_key: str) -> Union[Decimal, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as a Decimal or raises TypeError.
        """
        try:
            return Decimal(self.flattened[config_key])
        except KeyError:
            return None

    def get_float(self, config_key: str) -> Union[float, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as a float or raises TypeError.
        """
        try:
            return float(self.flattened[config_key])
        except KeyError:
            return None

    def get_int(self, config_key: str) -> Union[int, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as an int or raises TypeError.
        """
        try:
            return int(self.flattened[config_key])
        except KeyError:
            return None

    def get_list(self, config_key: str, csv: bool = True) -> Union[list, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as a list or raises TypeError. If csv is True
        (default), split value on commas.
        """
        try:
            value = self.flattened[config_key]
            if type(value) != list and csv is True:
                split = value.split(",")
                return [val.strip() for val in split]
            return list(value)
        except KeyError:
            return None

    def get_string(self, config_key: str) -> Union[str, None]:
        """
        Get a configuration value by its dotted path key; attempts to return
        the requested value as a string or raises TypeError.
        """
        try:
            return str(self.flattened[config_key])
        except KeyError:
            return None

    def set(self, config_key: str, value: ConfigValueType) -> None:
        """
        Explicitly set config_key (a dotted key string) to value. Values set
        via this method take precedence over all other configuration sources.
        """
        flat_dict = {config_key: value}
        expanded = utils.expand_flattened_dict(flat_dict)
        utils.merge_dicts(expanded, self.values["super"])

    def set_default(self, config_key: str, value: ConfigValueType) -> None:
        """
        Set the default value for config_key (a dotted key string) to value.
        Values set via this method will be overridden by any configuration
        provider containing a matching config_key.
        """
        flat_dict = {config_key: value}
        expanded = utils.expand_flattened_dict(flat_dict)
        utils.merge_dicts(expanded, self.values["defaults"])

    def update(self) -> None:
        """
        Updates configuration values from all providers.
        """
        self.providers.update_all()

    def _merge_configs(self) -> Dict:
        """
        Merges configuration from all configured providers into final config.
        """
        config = utils.merge_dicts(self.values["defaults"], {})
        for provider_name in self.providers.ordering:
            if provider := self.providers.get(provider_name):
                config = utils.merge_dicts(provider.dict, config)
        config = utils.merge_dicts(self.values["super"], config)
        return config
