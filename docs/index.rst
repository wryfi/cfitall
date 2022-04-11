.. cfitall documentation master file, created by
   sphinx-quickstart on Sun Apr 10 07:34:48 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Configure It All
================

.. toctree::
   :hidden:

   Home <self>
   Data Structures <datastructures>
   Configuration Registry <registry>
   Configuration Providers <providers>
   Provider Manager <manager>
   Reference <_autosummary/cfitall>

cfitall (configure it all) is a configuration library for Python applications,
loosely inspired by the `viper <https://github.com/spf13/viper>`__ library
for Go.

cfitall provides a *registry* for configuring your application from a series of
*providers*, which are managed by a *manager*. When requesting a configuration
value, data from each provider is merged into the next to resolve the requested
value. Providers can be easily written and registered to extend cfitall's
functionality.

Included with the package are a
:py:class:`~cfitall.providers.filesystem.FilesystemProvider`
and an :py:class:`~cfitall.providers.environment.EnvironmentProvider` for
reading configuration data from the filesystem or environment variables,
respectively.

Quick Start / Example
*********************

First, install cfitall from PyPi via your favorite package manager:

::

   pip install 'cfitall>=2.0'

For this example, we will configure a contrived application called
``myapp``, which we will also use as our registry name. The
FilesystemProvider and EnvironmentProvider both use this value as a namespace.

Our configuration file will therefore be named ``myapp.(json|yaml|yml)``. By
default, the FilesystemProvider will search for a matching file first in
``$HOME/.local/etc/myapp`` and then in ``/etc/myapp``. Let's create a
configuration file in YAML format and put it in place:

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

The EnvironmentProvider also uses the registry name as a namespace, searching
environment variables beginning with ``MYAPP__`` for values. Let's export some
environment variables to see this provider in action:

::

    export MYAPP__GLOBAL__NAME="my app from bash"
    export MYAPP__GLOBAL__THINGS="[four, five, six]"
    export MYAPP__NETWORK__PORT=8080

Next, set up a ``ConfigurationRegistry`` for myapp, naming it ``myapp``.

::

    # myapp/__init__.py

    from cfitall.registry import ConfigurationRegistry


    # create a configuration registry for myapp
    config = ConfigurationRegistry('myapp')

    # set some default configuration values
    config.set_default('global.name', 'my fancy application')
    config.set_default('global.foo', 'bar')
    config.set_default('network.listen', '127.0.0.1')

    # read/update data from enabled providers
    config.update()


Now you can use your registry instance to get the configuration data you
need. You can access the merged configuration data by its configuration
key (dictionary keys separated by ``.``), or you can just grab the entire
merged dictionary via the ``dict`` property.

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


Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


