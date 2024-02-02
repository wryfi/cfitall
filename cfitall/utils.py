"""
This module is full of little recursive functions that help with
converting string-path notations into nested dicts, and vice
versa. A string-path, or "flattened" dict might look like this:

    {'foo.bar.bat': 'asdfhjklkjhfdsa'}

As an "expanded" or "nested" dict, the same data would be:

    {'foo': {'bar': {'bat': 'lkjhgfdsasdfghjkl'}}}
"""

from collections.abc import Mapping
from typing import Dict, Optional

from cfitall import ConfigValueType


def add_keys(
    destdict: dict, srclist: list, value: Optional[ConfigValueType] = None
) -> dict:
    """
    Nests keys from srclist into destdict, with optional value set on the final key.

    :param destdict: dictionary to add keys to
    :param srclist: list to add keys from
    :param value: final key's value
    """
    if len(srclist) > 1:
        destdict[srclist[0]] = {}
        destdict[srclist[0]] = destdict.get(srclist[0], {})
        add_keys(destdict[srclist[0]], srclist[1:], value)
    else:
        destdict[srclist[0]] = value
    return destdict


def expand_flattened_path(
    flattened_path: str, value: Optional[ConfigValueType] = None, separator: str = "."
) -> dict:
    """
    Expands a dotted path into a nested dict; if value is set, the
    final key in the path will be set to value.

    :param flattened_path: the dotted path to expand to a nested dict
    :param value: final key's value
    :param separator: separator between dict keys in flattened_path
    """
    split_list = flattened_path.split(separator)
    return add_keys({}, split_list, value)


def flatten_dict(nested: dict) -> dict:
    """
    Flattens a deeply nested dictionary into a flattened dictionary.
    For example `{'foo': {'bar': 'baz'}}` would be flattened to
    `{'foo.bar': 'baz'}`.

    :param nested: dictionary to flatten
    """
    flattened = {}
    for key, value in nested.items():
        if isinstance(value, Mapping):
            for subkey, subval in value.items():
                newkey = ".".join([key, subkey])
                flattened[newkey] = subval
            flatten_dict(flattened)
        else:
            flattened[key] = value
    mappings = [isinstance(value, Mapping) for key, value in flattened.items()]
    if len(set(mappings)) == 1 and set(mappings).pop() is False:
        return flattened
    elif len(set(mappings)) > 0:
        return flatten_dict(flattened)
    return {}


def merge_dicts(source: Mapping, destination: dict) -> dict:
    """
    Performs a deep merge of two nested dicts by expanding all Mapping objects
    until they reach a non-mapping value (e.g. a list, string, int, etc.) and
    copying these from the source to the destination.

    :param source: source dictionary to copy from
    :param destination: destination dict to merge into
    """
    for key, value in source.items():
        key = key.lower() if isinstance(key, str) else key
        if isinstance(value, Mapping):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            destination[key] = value
    return destination


def expand_flattened_dict(flattened: dict, separator: str = ".") -> dict:
    """
    Expands a flattened dict into a nested dict, e.g. {'foo.bar': 'baz'} to
    {'foo': {'bar': 'baz'}}.

    :param flattened: dictionary with flattened keys to expand
    :param separator: separator between dict keys in flattened_path
    """
    merged: Dict[str, ConfigValueType] = {}
    for key, value in flattened.items():
        expanded = expand_flattened_path(key, value=value, separator=separator)
        merged = merge_dicts(merged, expanded)
    return merged
