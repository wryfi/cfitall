import os
import unittest

from cfitall.config import ConfigRegistry


class TestConfigRegistry(unittest.TestCase):
    def setUp(self):
        super().setUp()
        os.environ['CFITALL__GLOBAL__NAME'] = 'cfitall'
        os.environ['CFITALL__GLOBAL__PATH'] = '/Users/wryfi,/Users/wryfi/tmp'
        os.environ['CFITALL__FOO__BANG'] = 'WHAMMY!'

    def tearDown(self):
        super().tearDown()
        del os.environ['CFITALL__GLOBAL__NAME']
        del os.environ['CFITALL__GLOBAL__PATH']
        del os.environ['CFITALL__FOO__BANG']

    def test_create_object(self):
        _registry = ConfigRegistry('cfitall')

    def test_environment_variables(self):
        registry = ConfigRegistry('cfitall')
        self.assertEqual(registry.get('global.name'), 'cfitall')
        self.assertEqual(registry.get('global.path', list), ['/Users/wryfi', '/Users/wryfi/tmp'])
        self.assertEqual(registry.get('foo.bang'), 'WHAMMY!')

    def test_config_file(self):
        registry = ConfigRegistry('cfitall')
        registry.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        registry.read_config()
        self.assertEqual(registry.get('global.name'), 'cfitall')
        self.assertEqual(registry.get('global.path', list), ['/Users/wryfi', '/Users/wryfi/tmp'])
        self.assertEqual(registry.get('foo.bang'), 'WHAMMY!')
        self.assertEqual(registry.get('global.authors', list), ['john doe', 'jane deer'])
        self.assertEqual(registry.get('search', list), ['/Users/wryfi/foo', '/Users/wryfi/bar'])
        self.assertEqual(registry.get('foo.bar'), 'baz')

    def test_config_order(self):
        registry = ConfigRegistry('cfitall')
        registry.set_default('global.authors', ['michael scott', 'jim halpert'])
        self.assertEqual(registry.get('global.authors', list), ['michael scott', 'jim halpert'])
        registry.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        registry.read_config()
        self.assertEqual(registry.get('global.authors', list), ['john doe', 'jane deer'])
        os.environ['CFITALL__GLOBAL__AUTHORS'] = 'carol cincinnati,robert california'
        self.assertEqual(registry.get('global.authors', list), ['carol cincinnati', 'robert california'])
        registry.set('global.authors', ['dwight schrute', 'pam beesly'])
        self.assertEqual(registry.get('global.authors', list), ['dwight schrute', 'pam beesly'])


if __name__ == '__main__':
    unittest.main()
