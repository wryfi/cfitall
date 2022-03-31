import os
import re
from typing import Union

from cfitall import utils
from base import ConfigProviderBase


class EnvironmentProvider(ConfigProviderBase):
    def __init__(
        self,
        prefix: str,
        cast_bool: bool = True,
        level_separator: str = "__",
        value_separator: str = ",",
        value_split: bool = True,
    ):
        """
        EnvironmentProvider attempts to read configuration values from environment
        variables.

        :param prefix: namespace prefix for environment variables (e.g. "myapp")
        :param cast_bool: attempt to cast "true" and "false" strings as booleans (True)
        :param level_separator: hierarchical separator in env variable name ("__")
        :param value_separator: string or regex to split lists on (",")
        :param value_split: whether to split values enclosed in square brackets (True)
        """
        self.provider_name = "environment"
        self.level_separator = level_separator
        self.value_separator = value_separator
        self.cast_bool = cast_bool
        self.value_split = value_split
        self.prefix = f"{prefix.upper()}{level_separator}"

    def _read_environment(self) -> dict:
        """
        Reads all environment variables beginning with prefix and loads them into
        a dictionary using level_separator as a hierarchical path separator.
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

    def _split_value(self, value: str) -> Union[list[str], str]:
        """
        If self.value_split is True, split value by self.value_separator,
        where value is a string of values enclosed in square brackets and separated
        by self.value_separator.
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
    def dict(self) -> dict:
        """
        Returns the provider's configuration data from environment variables.
        """
        return utils.expand_flattened_dict(
            self._read_environment(), separator=self.level_separator
        )

    def update(self) -> bool:
        """
        This is a no-op for the EnvironmentProvider, which always reads
        environment variables in realtime as doing so is a non-blocking call.
        """
        return True
