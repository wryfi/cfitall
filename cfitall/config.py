from decimal import Decimal
import logging
import json
import re
import os
import yaml

from cfitall import utils
from cfitall.providers.environment import EnvironmentProvider

logger = logging.getLogger(__name__)


class ConfigManager(object):
    def __init__(
        self,
        name,
        env_prefix=None,
        env_level_separator="__",
        env_value_split=True,
        env_value_separator=",",
        env_bool=True,
        defaults={},
    ):
        """
        The configuration registry holds configuration data from different sources
        and reconciles it for retrieval.

        :param str name: name of registry (cannot contain env_separator string)
        :param str env_prefix: prefix for environment variables (defaults to uppercase name)
        :param str env_level_separator: string for separating config hierarchies in env vars (default '__')
        :param bool env_value_split: split env var values into python list
        :param str env_value_separator: regex to split on if env_value_split is True (default ',')
        :param bool env_bool: convert 'true' and 'false' strings in env vars to python bools
        :param dict defaults: dictionary of default configuration settings
        """
        self.name = name
        self.config_file = None
        self.config_path = []
        self.values = {"super": {}, "cli": {}, "cfgfile": {}, "defaults": defaults}
        self.env_level_separator = env_level_separator
        self.env_value_split = env_value_split
        self.env_value_separator = env_value_separator
        self.env_bool = env_bool
        if env_prefix:
            self.env_prefix = env_prefix.upper()
        else:
            self.env_prefix = self.name.upper()

    @property
    def config_keys(self):
        """
        Returns a list of configuration keys as dotted paths, for
        use with the get() or set() methods.

        :return: list of configuration keys as dotted paths
        :rtype: list
        """
        config_keys = [key for key, value in self.flattened.items()]
        return sorted(config_keys)

    @property
    def dict(self):
        """
        Returns a dict of merged configuration data

        :return: merged dictionary of configuration data
        :rtype: dict
        """
        return self._merge_configs()

    @property
    def env_vars(self):
        """
        Returns a list of environment variables known from config files and defaults

        :return: list of environment variables that will be read
        :rtype: list
        """
        prefix = self.env_prefix + self.env_level_separator
        keys = [key.upper() for key, value in self.flattened.items()]
        keys = [prefix + key.replace(".", self.env_level_separator) for key in keys]
        return sorted(keys)

    @property
    def flattened(self):
        """
        Returns a "flattened" dictionary of merged config values,
        condensing hierarchies into dotted paths and returning simple
        key-value pairs.

        :return: flattened dictionary of merged config values
        :rtype: dict
        """
        return utils.flatten_dict(self.dict)

    @property
    def json(self):
        return json.dumps(self.dict, indent=4, sort_keys=True)

    @property
    def yaml(self):
        return yaml.dump(self.dict)

    def add_config_path(self, path):
        """
        Adds a path to search for a configuration file.  Currently
        limited to the local filesystem, s3 integration envisioned.

        :param path: filesystem path to search for config files
        :return: None
        """
        self.config_path.append(path)

    def get(self, config_key, rtype=None):
        """
        Get a configuration value by its dotted path key.  There
        must be an exact match for the value you request.

        :param config_key: dotted path key in the config registry
        :param rtype: requested return type (list, str, int, Decimal, float)
        :return: value from config registry corresponding to key
        """
        try:
            value = self.flattened[config_key]
        except KeyError:
            return None
        value_type = type(value)
        if rtype == list:
            return list(value)
        if rtype == str:
            if value_type == list:
                return ",".join(value)
            return str(value)
        elif rtype == int:
            return int(value)
        elif rtype == Decimal:
            return Decimal(value)
        elif rtype == float:
            return float(value)
        return value

    def set(self, config_key, value):
        """
        Explicitly set a configuration key via dotted key path.
        Configurations set this way take precedence over all other
        configuration sources.

        :param config_key: dotted path key to set
        :param value: value to set
        """
        flat_dict = {config_key: value}
        expanded = utils.expand_flattened_dict(flat_dict)
        utils.merge_dicts(expanded, self.values["super"])

    def set_default(self, config_key, value):
        """
        Set a default value in the registry via dotted key path.
        Configurations set this way are the first to be overriden by other
        configuration sources.

        :param config_key: dotted path key to set
        :param value: value to set
        :return:
        """
        flat_dict = {config_key: value}
        expanded = utils.expand_flattened_dict(flat_dict)
        utils.merge_dicts(expanded, self.values["defaults"])

    def read_config(self):
        """
        Search through the available paths in config_path and read the first
        suitable configuration file found.

        :return: True if a configuration file was read, else False
        :rtype: bool
        """
        for path in self.config_path:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if re.match("{}.json".format(self.name.lower()), file):
                        self.config_file = os.path.join(path, file)
                        self._read_json_file(self.config_file)
                        return True
                    if re.match("{}.ya*ml".format(self.name.lower()), file):
                        self.config_file = os.path.join(path, file)
                        self._read_yaml_file(self.config_file)
                        return True
        return False

    def _read_yaml_file(self, path):
        """
        Opens path as a yaml file and attempts to safely load it into the
        cfgfile value dictionary.

        :param path: path to yaml file
        """
        with open(path, "r") as fp:
            data = yaml.safe_load(fp.read())
        for key, value in data.items():
            self.values["cfgfile"][key.lower()] = value

    def _read_json_file(self, path):
        """
        Opens path as a json file and attempts to load it into the
        cfgfile value dictionary.

        :param path: path to json file
        """
        with open(path, "r") as fp:
            data = json.loads(fp.read())
        for key, value in data.items():
            self.values["cfgfile"][key.lower()] = value

    def _merge_configs(self):
        """
        Merges all of the configuration data together in the appropriate order.

        :return: merged configuration data
        :rtype: dict
        """
        envprovider = EnvironmentProvider(
            self.name,
            self.env_level_separator,
            self.env_value_separator,
            self.env_bool,
            self.env_value_split,
        )
        config = utils.merge_dicts(self.values["defaults"], {})
        config = utils.merge_dicts(self.values["cfgfile"], config)
        config = utils.merge_dicts(envprovider.dict, config)
        config = utils.merge_dicts(self.values["super"], config)
        return config
