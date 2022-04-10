cfitall :: configure it all
===========================

cfitall (configure it all) is a configuration management library for
python applications. It's inspired by the
`viper <https://github.com/spf13/viper>`__ library for go.

cfitall provides a registry for configuring your application from a
combination of providers, with a configurable inheritance hierarchy, merging
data from each provider to retrieve a requested value.

The registry itself holds the default configuration values and
developer-overridden values, and manages additional configuration providers in
between.

This package includes two such configuration providers:

- The ``EnvironmentProvider``, which parses environment variables for configuration data
- The ``FilesystemProvider``, which parses json or yaml files for configuration data

Any provider implementing ``cfitall.providers.base.ConfigProviderBase`` can be
added to the registry by calling ``<registry>.providers.register(<Provider>)``.
Providers are merged into the final configuration in the order they are
registered.

The ``ConfigurationRegistry`` requires a single argument: a name that will be
used to identify and namespace the configuration. With no additional arguments,
the constructor will return an instance with a FilesystemProvider and an
EnvironmentProvider configured with default values. The assembled configuration
from the default configuration will consider the following configuration sources
in order:

-  default values provided by the developer via ``set_default()``
-  the first JSON or YAML configuration file found in
   ``$HOME/.local/etc/{name}/{name}.(json|yaml|yml)`` or
   ``/etc/{name}/{name}.(json|yaml|yml)`` (values override defaults)
-  environment variables (override configuration file values & defaults)
-  ``set()`` calls made by the developer (override everything)

To disable the ``EnvironmentProvider`` or ``FilesystemProvider``, or to
customize the providers at instance construction time, you can pass
the constructor an optional list of providers. For example,
``cf = ConfigurationRegistry("test", providers=[])`` will create a
configuration registry that only provides default values and
developer overrides.

Alternatively, call the ``providers.deregister(<provider_name>)`` method on
the registry.


Install
-------

``pip install cfitall`` should do the trick for most users. cfitall
requires python3 but otherwise has minimal dependencies.

To build a package for debian/ubuntu, `stdeb <https://pypi.org/project/stdeb/>`__
works well:

::

    apt install python3-all python3-stdeb python3-pbr
    setup.py --command-packages=stdeb.command sdist_dsc --debian-version bionic1 bdist_deb

Example
-------

This example is for a contrived application called ``myapp``.

Since we chose ``myapp`` as our config manager name, our
configuration file is also named ``myapp.(json|yaml|yml)``. Create a
configuration file in YAML or JSON and put it in place:

::

    # ~/.local/etc/myapp/myapp.yml
    global:
      bar: foo
      things:
        - one
        - two
        - three
      person:
        name: joe
        hair: brown
    network:
      port: 9000
      listen: '*'


Next, set up a ``ConfigurationRegistry`` for myapp. Notice that we name our
registry ``myapp``.

::

    # myapp/__init__.py

    from cfitall.registry import ConfigurationRegistry

    # create a configuration registry for myapp
    config = ConfigurationRegistry('myapp')

    # set some default configuration values
    config.set_default('global.name', 'my fancy application')
    config.set_default('global.foo', 'bar')
    config.set_default('network.listen', '127.0.0.1')

    # add an additional path to search for configuration files
    config.providers.filesystem.path.append('/etc/somewhere')

    # read/update data from enabled providers
    config.update()

Since we named our config object ``myapp``, environment variables
beginning with ``MYAPP__`` are searched for values by ``EnvironmentProvider``.
Environment variable values in square brackets are by default parsed as
comma-delimited lists. Export some environment variables to see this in
action:

::

    export MYAPP__GLOBAL__NAME="my app from bash"
    export MYAPP__GLOBAL__THINGS="[four, five, six]"
    export MYAPP__NETWORK__PORT=8080

Now you can use your config object to get the configuration data you
need. You can access the merged configuration data by its configuration
key (dotted path notation), or you can just grab the entire merged
dictionary via the ``dict`` property.

::

    # myapp/logic.py

    from myapp import config

    # prints ['four', 'five', 'six'] because env var overrides config file
    print(config.get('global.things'))

    # prints 8080 because env var overrides config file
    print(config.get_int('network.port'))

    # prints * because config file overrides default set by set_default()
    print(config.get_str('network.listen'))

    # prints 'joe' from myapp.yml because it is only defined there
    print(config.get('global.person.name'))

    # alternate way to print joe through the config dict property
    print(config.dict['global']['person']['name'])

    # prints the entire assembled config as dictionary
    print(config.dict)

Running ``logic.py`` should go something like this:

::

    $ python logic.py
    ['four', 'five', 'six']
    8080
    *
    joe
    joe
    {'global': {'name': 'my app from bash', 'foo': 'bar', 'bar': 'foo', 'things': ['four', 'five', 'six'], 'person': {'name': 'joe', 'hair': 'brown'}}, 'network': {'listen': '*', 'port': '8080'}}

EnvironmentProvider
-------------------

Environment variables matching the pattern ``MYAPP__.*`` are
automatically read into the configuration, where ``MYAPP`` refers to
the uppercased ``name`` given to your registry at creation.

-  You can customize this behavior by creating your own instance of an
   ``EnvironmentProvider``.

By default ``__`` (double-underscore) is parsed as a hierarchical separator.
After stripping the application prefix from the variable name, the ``__``
is effectively equivalent to a ``.`` in dotted-path notation e.g.
``MYAPP__GLOBAL__THINGS`` is equivalent to ``global.things``.

-  You can customize the string used as hierarchical separator,
   replacing ``__`` with a string of your choosing, by passing
   a ``level_separator`` keyword argument to your ``EnvironmentProvider``,
   e.g.
   ``provider = EnvironmentProvider(level_separator='____')`` (four underscores).
   Bear in mind that environment variable keys are limited to alphanumeric
   ASCII characters and underscores (no hyphens, dots, or other punctuation),
   and must start with a letter.

-  NOTE: Avoid using the value of ``level_separator`` in your configuration
   keys (names), as this will confuse the provider's parsing.

String values of "true" or "false" (in any combination of upper/lower case)
are cast to python booleans by default.

- To disable this behavior, pass ``cast_bool=False`` to the ``EnvironmentManager``
  constructor.

Values that are enclosed in square brackets are parsed as comma-separated
lists by default. For example, if you ``export MYAPP__FOO="[a, b, c]"`` the
parsed value of foo will be a python list, ``['a', 'b', 'c']``.

- You can disable list parsing by passing ``value_split=False`` to
  to the ``EnvironmentProvider`` constructor, in which case the above would return a
  python string, ``"[a, b, c]"``.

- You can customize the value separator by passing a ``value_separator``
  keyword to the ``EnvironmentProvider`` constructor. The separator is treated as a
  regex, so you can use e.g. ``value_separator=r'\s+'`` to split on
  whitespace instead of the default comma.
