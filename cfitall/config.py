from decimal import Decimal
import json
import re
import os
import yaml

from cfitall import utils


class ConfigManager(object):
    def __init__(self, name, env_prefix=None, env_path_sep='__', env_value_split=True, env_bool=True, defaults={}):
        """
        The configuration registry holds configuration data from different sources
        and reconciles it for retrieval.

        :param str name: name of registry (cannot contain env_separator string)
        :param str env_prefix: prefix for environment variables (defaults to uppercase name)
        :param str env_path_sep: string for separating config hierarchies in env vars (default '__')
        :param bool env_value_split: split env var values into python string (on comma)
        :param bool env_bool: convert 'true' and 'false' strings in env vars to python bools
        :param dict defaults: dictionary of default configuration settings
        """
        self.name = name
        self.config_file = None
        self.config_path = []
        self.values = {'super': {}, 'cli': {}, 'cfgfile': {}, 'defaults': defaults}
        self.env_path_sep = env_path_sep
        self.env_value_split = env_value_split
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
        prefix = self.env_prefix + self.env_path_sep
        keys = [key.upper() for key, value in self.flattened.items()]
        keys = [prefix + key.replace('.', self.env_path_sep) for key in keys]
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
                return ','.join(value)
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
        utils.merge_dicts(expanded, self.values['super'])

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
        utils.merge_dicts(expanded, self.values['defaults'])

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
                    if re.match('{}.json'.format(self.name.lower()), file):
                        self.config_file = os.path.join(path, file)
                        self._read_json_file(self.config_file)
                        return True
                    if re.match('{}.ya*ml'.format(self.name.lower()), file):
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
        with open(path, 'r') as fp:
            data = yaml.safe_load(fp.read())
        for key, value in data.items():
            self.values['cfgfile'][key.lower()] = value

    def _read_json_file(self, path):
        """
        Opens path as a json file and attempts to load it into the
        cfgfile value dictionary.

        :param path: path to json file
        """
        with open(path, 'r') as fp:
            data = json.loads(fp.read())
        for key, value in data.items():
            self.values['cfgfile'][key.lower()] = value

    def _read_environment(self):
        """
        Reads all environment variables beginning with env_prefix and loads
        them into a dictionary using env_separator as a hierarchical path
        separator.

        :return: config dictionary read from environment variables
        :rtype: dict
        """
        output = {}
        prefix = self.env_prefix + self.env_path_sep
        for key, value in os.environ.items():
            if key.startswith(prefix):
                key = key.replace(prefix, '', 1).lower()
                if isinstance(value, str) and self.env_value_split:
                    if re.match(r'.*,(.*,)*.*', value):
                        value = value.split(',')
                if self.env_bool:
                    if type(value) == str and value.lower() == 'true':
                        value = True
                    if type(value) == str and value.lower() == 'false':
                        value = False
                    if type(value) == list:
                        value = [True if type(val) == str and val.lower() == 'true' else val for val in value]
                        value = [False if type(val) == str and val.lower() == 'false' else val for val in value]
                output[key] = value
        return utils.expand_flattened_dict(output, separator=self.env_path_sep)

    def _merge_configs(self):
        """
        Merges all of the configuration data together in the appropriate order.

        :return: merged configuration data
        :rtype: dict
        """
        config = utils.merge_dicts(self.values['defaults'], {})
        config = utils.merge_dicts(self.values['cfgfile'], config)
        config = utils.merge_dicts(self._read_environment(), config)
        config = utils.merge_dicts(self.values['super'], config)
        return config
