Configuration Registry
======================

The :py:class:`~cfitall.registry.ConfigurationRegistry` is the main entry point
into the library and the class developers will interact with most frequently.

Default Behavior
****************

Its constructor requires a single argument: a name that will be
used to identify and namespace the configuration (the name of your application
is usually a good choice).

With no additional arguments, the constructor will
return a registry with a
:py:class:`~cfitall.providers.filesystem.FilesystemProvider` and an
:py:class:`~cfitall.providers.environment.EnvironmentProvider` configured to
sane defaults, which will consider the following configuration sources in order:

* default values provided by the developer:

  * ``defaults`` passed in to the :py:class:`~cfitall.registry.ConfigurationRegistry` constructor
  * programmatic calls to the registry's :py:meth:`~cfitall.registry.ConfigurationRegistry.set_default` method

* the first JSON or YAML configuration file found from:

  * ``$HOME/.local/etc/{name}/{name}.(json|yaml|yml)``
  * ``/etc/{name}/{name}.(json|yaml|yml)``

* environment variables in the ``{NAME}__`` namespace
* developer overrides via the registry's :py:meth:`~cfitall.registry.ConfigurationRegistry.set` method

Providers
*********

The registry merges configurations from a set of providers. These providers are
managed by a :py:class:`~cfitall.manager.ProviderManager`, which is attached to
the registry as its :py:attr:`~cfitall.registry.ConfigurationRegistry.providers`
attribute.

To disable or customize the default providers, you can pass the registry constructor
your own list of providers (which can be empty). For example,
``cf = ConfigurationRegistry("app", providers=[])`` will create a configuration
registry that only manages default values and developer overrides.

Alternatively, you can call the :py:meth:`~cfitall.manager.ProviderManager.register`
or :py:meth:`~cfitall.manager.ProviderManager.deregister` methods on the registry's
:py:attr:`provider manager <cfitall.registry.ConfigurationRegistry.providers>` to
add or remove a provider (e.g. ``cf.providers.deregister("environment")``).

Provider Values
---------------

Each provider is required to implement an
:py:meth:`~cfitall.providers.base.ConfigProviderBase.update` method that will
trigger it to read its configuration from the source and update itself
accordingly.

In the case of the :py:class:`~cfitall.providers.filesystem.FilesystemProvider`,
for example, the :py:meth:`~cfitall.providers.filesystem.FilesystemProvider.update`
method causes the provider to read the first configuration file it finds from
the filesystem.

Always call :py:meth:`~cfitall.registry.ConfigurationRegistry.update` on your
registry after constructing it. This will call each provider's ``update()``
method, which some providers require.


Getting Values
**************

A dictionary of merged configuration values is available as the registry's
:py:attr:`~cfitall.registry.ConfigurationRegistry.dict` property.

An individual value can be retrieved using the
:py:meth:`~cfitall.registry.ConfigurationRegistry.get` method, which takes a
configuration key as its argument and returns the value in its stored type.

Additional helper functions to cast the value to various types are included
(e.g. :py:meth:`~cfitall.registry.ConfigurationRegistry.get_bool`).
