from decimal import Decimal
from typing import Union

from cfitall.providers.environment import EnvironmentProvider
from cfitall.providers.filesystem import FilesystemProvider

ConfigValueType = Union[bool, Decimal, float, int, list, str]
ConfigProviderType = Union[EnvironmentProvider, FilesystemProvider]
