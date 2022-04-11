"""
implements a FilesystemProvider for reading configs from disk
"""

import json
import logging
import os
from typing import Union, List

import yaml

from cfitall.providers.base import ConfigProviderBase

logger = logging.getLogger(__name__)


class FilesystemProvider(ConfigProviderBase):
    #: list of filesystem locations to search for config files
    path: List[str]
    #: namespace for locating files
    prefix: str

    def __init__(
        self, path: list[str], prefix: str, provider_name: str = "filesystem"
    ) -> None:
        """
        FilesystemProvider attempts to read json or yaml configuration files
        from disk.

        :param path: list of filesystem paths to search for config files
        :param prefix: base name of file to look for (e.g. f"{prefix}.yml")
        :param provider_name: friendly name for the provider ("filesystem")
        """
        self.path = path
        self.prefix = prefix
        self.provider_name = provider_name
        self.config_file: Union[str, None] = None
        self.config_file_type: Union[str, None] = None
        self._set_config_file()
        self._data: dict = {}

    def _read_config_file(self) -> None:
        """
        Attempts to read and parse self.config_file, storing the results
        in the self._data dictionary.
        """
        if self.config_file and os.path.isfile(self.config_file):
            try:
                with open(self.config_file, "r") as file_:
                    data = {}
                    if self.config_file_type == "yaml":
                        data = yaml.safe_load(file_.read())
                    elif self.config_file_type == "json":
                        data = json.loads(file_.read())
            except Exception as ex:
                logger.error(f"error opening file: {self.config_file}: {ex}")
            self._data = {key.lower(): value for key, value in data.items()}
        else:
            logger.warning("config_file not set or file does not exist")

    def _set_config_file(self) -> bool:
        """
        Iterates through the directories in self.path, looking for json or yaml
        configuration files, and configuring the object to use the first found.
        Returns True if a file is found, else returns False.
        """
        for path in self.path:
            if os.path.isdir(path):
                for file in sorted(os.listdir(path)):
                    if file == f"{self.prefix.lower()}.json":
                        self.config_file = os.path.join(path, file)
                        self.config_file_type = "json"
                        return True
                    elif (
                        file == f"{self.prefix.lower()}.yaml"
                        or file == f"{self.prefix.lower()}.yml"
                    ):
                        self.config_file = os.path.join(path, file)
                        self.config_file_type = "yaml"
                        return True
        return False

    def update(self) -> bool:
        """
        Updates self._data from the contents of self.config_file.
        """
        if self._set_config_file():
            self._read_config_file()
            return True
        return False

    @property
    def dict(self) -> dict:
        """
        Returns the configuration dictionary from self._data.
        """
        return self._data
