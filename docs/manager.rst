Provider Manager
================

Each instance of a :py:class:`~cfitall.registry.ConfigurationRegistry` has a
:py:class:`~cfitall.manager.ProviderManager` as its
:py:attr:`~cfitall.registry.ConfigurationRegistry.providers` attribute. The
manager keeps track of the providers that the registry will use to resolve its final
configuration values.

To add a provider, call the :py:meth:`~cfitall.manager.ProviderManager.register`
method of the manager, passing in an object that implements
:py:class:`~cfitall.providers.base.ConfigProviderBase`.

Registering a provider does two things:

* Adds the provider instance as an attribute of the manager, named
  after the provider's
  :py:attr:`~cfitall.providers.base.ConfigProviderBase.provider_name`.
* Appends the the ``provider_name`` to the manager's
  :py:attr:`~cfitall.manager.ProviderManager.ordering` attribute

To remove a provider, simply call :py:meth:`~cfitall.manager.ProviderManager.deregister`
with the ``provider_name``, and the reverse process will be performed.

Merge Order
***********

When assembling the final configuration dictionary, the manager's
:py:attr:`~cfitall.manager.ProviderManager.ordering` property
determines the order in which providers are merged. By default the most recently
registered provider has the highest precedence.

You can update the :py:attr:`~cfitall.manager.ProviderManager.ordering`
attribute to change the order in which provider dictionaries are merged (just
like any other Python list).
