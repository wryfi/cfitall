Configuration Providers
=======================

A Configuration Provider implements
:py:class:`~cfitall.providers.base.ConfigProviderBase`, allowing it to be
registered by a :py:class:`~cfitall.manager.ProviderManager` and thereby
included in a :py:class:`~cfitall.registry.ConfigurationRegistry`.

Two such Providers are included in this package:

- The :py:class:`~cfitall.providers.environment.EnvironmentProvider` parses
  environment variables for configuration data.
- The :py:class:`~cfitall.providers.filesystem.FilesystemProvider` parses json
  or yaml files for configuration data.

Any provider implementing :py:class:`~cfitall.providers.base.ConfigProviderBase`
can be added to the registry by calling the
:py:meth:`~cfitall.manager.ProviderManager.register` method on the registry's
:py:attr:`manager <cfitall.registry.ConfigurationRegistry.providers>`.

Environment Provider
********************

The :py:class:`~cfitall.providers.environment.EnvironmentProvider` attempts to
automatically parse configuration data for your application from environment
variables.

Environment variables matching the pattern ``APP__.*`` are
automatically read into the configuration, where ``APP`` refers to
the uppercased ``name`` given to your registry at creation.

*  You can customize this behavior by creating your own instance of an
   :py:class:`~cfitall.providers.environment.EnvironmentProvider`.

By default ``__`` (double-underscore) is parsed as a hierarchical separator.
After stripping the application prefix from the variable name, the ``__``
is effectively equivalent to a ``.`` in dotted-path notation e.g.
``APP__GLOBAL__THINGS`` is equivalent to ``global.things``, which is the same
as ``{"global": {"things": {}}}``.

*  You can customize the string used as hierarchical separator,
   replacing ``__`` with a string of your choosing, by passing
   a ``level_separator`` keyword argument to your
   :py:class:`~cfitall.providers.environment.EnvironmentProvider`,
   e.g.
   ``provider = EnvironmentProvider(level_separator='____')`` (four underscores).
   Bear in mind that environment variable keys are limited to alphanumeric
   ASCII characters and underscores (no hyphens, dots, or other punctuation),
   and must start with a letter.

*  NOTE: Avoid using the value of ``level_separator`` in your configuration
   keys (names), as this will confuse the provider's parsing.

String values of "true" or "false" (in any combination of upper/lower case)
are cast to python booleans by default.

* To disable this behavior, pass ``cast_bool=False`` to the
  :py:class:`~cfitall.providers.environment.EnvironmentProvider` constructor.

Values that are enclosed in square brackets are parsed as comma-separated
lists by default. For example, if you ``export APP__FOO="[a, b, c]"`` the
parsed value of foo will be a python list, ``['a', 'b', 'c']``.

* You can disable list parsing by passing ``value_split=False`` to
  to the :py:class:`~cfitall.providers.environment.EnvironmentProvider` constructor,
  in which case the above would return a python string: ``"[a, b, c]"``.

* You can customize the value separator by passing a ``value_separator``
  keyword to the
  :py:class:`~cfitall.providers.environment.EnvironmentProvider` constructor.
  The separator is treated as a regex, so you can use e.g. ``value_separator=r'\s+'``
  to split on whitespace instead of the default comma.


Filesystem Provider
*******************

The :py:class:`~cfitall.providers.filesystem.FilesystemProvider` searches a list
of filesystem paths for JSON or YAML configuration files, parses the first one
that it finds, and stores the configuration in memory until its ``update()`` method
is called again.

If a list of paths is not specified, the provider will search for files as follows:

* ``$HOME/.local/etc/{prefix}/{prefix}.(json|yaml|yml)``
* ``/etc/{prefix}/{prefix}.(json|yaml|yml)``

The list of paths is stored as a list on the provider's
:py:attr:`~cfitall.providers.filesystem.FilesystemProvider.path` attribute, and
can be manipulated just like any other list to add or remove paths to search.
