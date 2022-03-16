cfitall :: configure it all
===========================

.. image:: https://travis-ci.org/wryfi/cfitall.svg?branch=develop
    :target: https://travis-ci.org/wryfi/cfitall

cfitall (configure it all) is a configuration management library for
python applications. It's inspired by and loosely modeled on the
excellent `viper <https://github.com/spf13/viper>`__ library for go,
though it doesn't have quite as many features (yet).

It does cover the basics of configuring your application from a combination
of sources, with a predictable inheritance hierarchy. It does this by
creating a configuration registry for your application, merging data from the
following sources to retrieve a requested value:

-  default values provided by the developer
-  YAML or JSON configuration file (values override defaults)
-  environment variables (override configuration file values & defaults)
-  ``set()`` calls made by the developer (override everything)

(Support for command-line and k/v store data sources is intended for the future;
pull requests welcome.)

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

First, set up a ``config`` module for myapp. Notice that we name our
config object ``myapp``.

::

    # myapp/__init__.py

    from cfitall.config import ConfigManager

    # create a configuration registry for myapp
    config = ConfigManager('myapp')

    # set some default configuration values
    config.set_default('global.name', 'my fancy application')
    config.set_default('global.foo', 'bar')
    config.set_default('network.listen', '127.0.0.1')

    # add a path to search for configuration files
    config.add_config_path('/Users/wryfi/.config/myapp')

    # read data from first config file found (myapp.json, myapp.yaml, or myapp.yml)
    config.read_config()

Since we named our config object ``myapp``, environment variables
beginning with ``MYAPP__`` are searched for values by cfitall.
Environment variables containing commas are interpreted as
comma-delimited lists. Export some environment variables to see this in
action:

::

    export MYAPP__GLOBAL__NAME="my app from bash"
    export MYAPP__GLOBAL__THINGS="[four, five, six]"
    export MYAPP__NETWORK__PORT=8080

Again, since we chose ``myapp`` as our config object name, our
configuration file is also named ``myapp.(json|yaml|yml)``. Create a
configuration file in YAML or JSON and put it in one of the paths you
added to your config registry:

::

    # ~/.config/myapp/myapp.yml
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

Now you can use your config object to get the configuration data you
need. You can access the merged configuration data by its configuration
key (dotted path notation), or you can just grab the entire merged
dictionary via the ``dict`` property.

::

    # myapp/logic.py

    from myapp import config

    # prints ['four', 'five', 'six'] because env var overrides config file
    print(config.get('global.things', list))

    # prints 8080 because env var overrides config file
    print(config.get('network.port', int))

    # prints * because config file overrides default set by set_default()
    print(config.get('network.listen', str))

    # prints 'joe' from myapp.yml because it is only defined there
    print(config.get('global.person.name', str))

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

Environment Variables
---------------------

By default ``__`` (double-underscore) is parsed as a hierarchical separator.
After stripping the application prefix from the variable name, the ``__``
is effectively equivalent to a ``.`` in dotted-path notation e.g.
``MYAPP__GLOBAL__THINGS`` is equivalent to ``global.things``.

-  You can customize the string used as hierarchical separator,
   replacing ``__`` with a string of your choosing, by passing
   an ``env_level_separator`` keyword argument to the ``ConfigManager``
   constructor, e.g.
   ``config = ConfigManager(env_level_separator='____')`` (four underscores).
   Bear in mind that environment variable names are limited to alphanumeric
   ASCII characters and underscores (no hyphens, dots, or other punctuation),
   and must start with a letter.

-  NOTE: Avoid using the value of ``env_level_separator`` in your configuration
   keys (names), as this will confuse cfitall's parsing!

Environment variables matching the pattern ``MYAPP__.*`` are
automatically read into the configuration, where ``MYAPP`` refers to
the uppercased ``name`` given to your ConfigManager at creation.

-  You can customize this behavior by passing an ``env_prefix`` value
   as a kwarg to the ConfigManager constructor, allowing you to set
   a value of your choosing in place of ``MYAPP`` (the ``__`` comes
   from the value of ``env_level_separator``, as described above).

String values of "true" or "false" (in any combination of upper/lower case)
are cast to python booleans.

- To disable this behavior, pass ``env_bool=False`` to the ``ConfigManager``
  constructor.

Values that are enclosed in square brackets are parsed as comma-separated
lists by default. For example, if you ``export MYAPP__FOO="[a, b, c]"`` the
parsed value of foo will be a python list, ``['a', 'b', 'c']``.

- You can disable list parsing by passing ``env_value_split=False`` to
  to the ``ConfigManager`` constructor.

- You can customize the value separator by passing an ``env_value_separator``
  keyword to the ``ConfigManager`` constructor. The separator is treated as a
  regex, so you can use e.g. ``env_value_separator=r'\s+'`` to split on
  whitespace instead of the default comma.



Development
-----------

cfitall uses modern python tooling with the pipenv dependency/environment
manager and pbr packaging system.

