Data Structures
===============

cfitall manages data stored in dictionaries.

The :py:class:`~cfitall.registry.ConfigurationRegistry` contains an internal
:py:attr:`~cfitall.registry.ConfigurationRegistry.values`
dictionary, where it holds configuration data for default values and
developer-overridden values. Likewise,
:py:class:`providers <cfitall.providers.base.ConfigProviderBase>` are
expected to provide a dictionary of values to the registry via their
:py:attr:`~cfitall.providers.base.ConfigProviderBase.dict` property.

When a configuration value is requested, the dictionaries are merged together
in a deterministic order, each overriding the last:

- First, the ``defaults`` from the registry's values dictionary are considered
- Then each provider's ``dict`` attribute, in the order listed in
  the :py:class:`manager's <cfitall.manager.ProviderManager>`
  :py:attr:`~cfitall.manager.ProviderManager.ordering` attribute
- Finally ``super`` values from the registry's values dictionary

The merged configuration dictionary can be accessed directly via the registry's
:py:attr:`~cfitall.registry.ConfigurationRegistry.dict` property; individual
values can also be retrieved by passing the registry's
:py:meth:`~cfitall.registry.ConfigurationRegistry.get` method (or one of its
typed variants) a valid configuration key.


Dotted Paths / Configuration Keys
*********************************

For convenience, dictionary keys are "flattened" into a *dotted path notation*,
also referred to as a *configuration key*, in a number of contexts throughout
the library:

::

    from cfitall.registry import ConfigurationRegistry
    cf = ConfigurationRegistry("app")

    # services.database.port is a configuration key / dotted path notation
    cf.set_default("services.database.port", 5432)

    # the configuration key is a concatenation of dictionary keys
    assert cf.get("services.database.port") == cf.dict["services"]["database"]["port"]

You can view a list of configuration keys (that the registry is aware of) by
inspecting the registry's :py:attr:`~cfitall.registry.ConfigurationRegistry.config_keys`
property.