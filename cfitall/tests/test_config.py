import os
import unittest

from cfitall.config import ConfigManager


class TestConfigManager(unittest.TestCase):
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
        _cf = ConfigManager('cfitall')

    def test_environment_variables(self):
        cf = ConfigManager('cfitall')
        self.assertEqual(cf.get('global.name'), 'cfitall')
        self.assertEqual(cf.get('global.path', list), ['/Users/wryfi', '/Users/wryfi/tmp'])
        self.assertEqual(cf.get('foo.bang'), 'WHAMMY!')

    def test_config_file(self):
        cf = ConfigManager('cfitall')
        cf.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        cf.read_config()
        self.assertEqual(cf.get('global.name'), 'cfitall')
        self.assertEqual(cf.get('global.path', list), ['/Users/wryfi', '/Users/wryfi/tmp'])
        self.assertEqual(cf.get('foo.bang'), 'WHAMMY!')
        self.assertEqual(cf.get('global.authors', list), ['john doe', 'jane deer'])
        self.assertEqual(cf.get('search', list), ['/Users/wryfi/foo', '/Users/wryfi/bar'])
        self.assertEqual(cf.get('foo.bar'), 'baz')

    def test_config_order(self):
        cf = ConfigManager('cfitall')
        cf.set_default('global.authors', ['michael scott', 'jim halpert'])
        self.assertEqual(cf.get('global.authors', list), ['michael scott', 'jim halpert'])
        cf.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        cf.read_config()
        self.assertEqual(cf.get('global.authors', list), ['john doe', 'jane deer'])
        os.environ['CFITALL__GLOBAL__AUTHORS'] = 'holly flax,robert california'
        self.assertEqual(cf.get('global.authors', list), ['holly flax', 'robert california'])
        cf.set('global.authors', ['dwight schrute', 'pam beesly'])
        self.assertEqual(cf.get('global.authors', list), ['dwight schrute', 'pam beesly'])


if __name__ == '__main__':
    unittest.main()
