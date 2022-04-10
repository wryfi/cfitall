from decimal import Decimal
from typing import Union

from cfitall.providers import EnvironmentProvider, FilesystemProvider

ConfigValueType = Union[bool, Decimal, float, int, list, str]
ConfigProviderType = Union[EnvironmentProvider, FilesystemProvider]
