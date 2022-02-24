"""
This module is full of little recursive functions that help with
converting string-path notations into nested dicts, and vice
versa. A string-path, or "flattened" dict might look like this:

    {'foo.bar.bat': 'asdfhjklkjhfdsa'}

As an "expanded" or "nested" dict, the same data would be:

    {'foo': {'bar': {'bat': 'lkjhgfdsasdfghjkl'}}}
"""

from collections.abc import Mapping


def add_keys(destdict, srclist, value=None):
    """
    Nests keys from srclist into destdict, with optional value set on the final key.

    :param dict destdict: the dict to update with values from srclist
    :param list srclist: list of keys to add to destdict
    :param value: final value to set
    :return: destination dictionary
    :rtype: dict
    """
    if len(srclist) > 1:
        destdict[srclist[0]] = {}
        destdict[srclist[0]] = destdict.get(srclist[0], {})
        add_keys(destdict[srclist[0]], srclist[1:], value)
    else:
        destdict[srclist[0]] = value
    return destdict


def expand_flattened_path(flattened_path, value=None, separator="."):
    """
    Expands a dotted path into a nested dict; if value is set, the
    final key in the path will be set to value.

    :param str flattened_path: flattened path to expand
    :param str separator: character(s) separating path components
    :param value: set final key to this value
    :return: nested dictionary
    :rtype: dict
    """
    split_list = flattened_path.split(separator)
    return add_keys({}, split_list, value)


def flatten_dict(nested):
    """
    Flattens a deeply nested dictionary into a flattened dictionary.
    For example `{'foo': {'bar': 'baz'}}` would be flattened to
    `{'foo.bar': 'baz'}`.

    :param dict nested: nested dictionary of configuration data
    :rtype: dict
    :return: dict of key-value pairs
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
    else:
        return flatten_dict(flattened)


def merge_dicts(source, destination):
    """
    Performs a deep merge of two nested dicts by expanding all Mapping objects
    until they reach a non-mapping value (e.g. a list, string, int, etc.) and
    copying these from the source to the destination.

    :param dict source: the source dictionary to copy values from
    :param dict destination: the dictionary to update with values from source
    :return: destination
    :rtype: dict
    """
    for key, value in source.items():
        key = key.lower() if isinstance(key, str) else key
        if isinstance(value, Mapping):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            destination[key] = value
    return destination


def expand_flattened_dict(flattened, separator="."):
    """
    Expands a flattened dict into a nested dict.

    :param dict flattened: the flattened dict to expand
    :param str separator: character used for separating paths in flattened dict
    :return: nested dict
    :rtype: dict
    """
    merged = {}
    for key, value in flattened.items():
        expanded = expand_flattened_path(key, value=value, separator=separator)
        merged = merge_dicts(merged, expanded)
    return merged
