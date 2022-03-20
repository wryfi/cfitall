import os
import re

from cfitall import utils
from cfitall.providers import ConfigProviderBase


class EnvironmentProvider(ConfigProviderBase):
    def __init__(
        self, name, level_separator, value_separator, cast_bool=True, value_split=True
    ):
        self.name = name
        self.level_separator = level_separator
        self.value_separator = value_separator
        self.cast_bool = cast_bool
        self.value_split = value_split
        self.prefix = f"{name.upper()}{level_separator}"

    def _read_environment(self):
        """
        Reads all environment variables beginning with prefix and loads
        them into a dictionary using level_separator as a hierarchical path
        separator.

        :return: config dictionary read from environment variables
        :rtype: dict
        """
        output = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                key = key.replace(self.prefix, "", 1).lower()
                value = self._split_value(value)
                if self.cast_bool:
                    if type(value) == str and value.lower() == "true":
                        value = True
                    if type(value) == str and value.lower() == "false":
                        value = False
                    if type(value) == list:
                        value = [
                            True if type(val) == str and val.lower() == "true" else val
                            for val in value
                        ]
                        value = [
                            False
                            if type(val) == str and val.lower() == "false"
                            else val
                            for val in value
                        ]
                output[key] = value
        return output

    def _split_value(self, value):
        """
        If self.value_split is True, split value by self.value_separator,
        where value is a string of values enclosed in square brackets and separated
        by self.value_separator.

        :param str value: string containing a list of values enclosed in square brackets
        :return: list of values obtained by splitting bracketed substring by self.value_separator
        :rtype: list || string
        """
        if self.value_split:
            if value.startswith("[") and value.endswith("]"):
                values = []
                for val in re.split(self.value_separator, value[1:-1]):
                    if val := val.strip():
                        values.append(val)
                return values
        return value

    @property
    def dict(self):
        return utils.expand_flattened_dict(
            self._read_environment(), separator=self.level_separator
        )
