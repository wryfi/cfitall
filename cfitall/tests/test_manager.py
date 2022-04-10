import unittest

from cfitall.manager import ProviderManager
from cfitall.providers import EnvironmentProvider
from cfitall.providers import FilesystemProvider


class ProviderManagerTests(unittest.TestCase):
    def test_init_empty(self):
        manager = ProviderManager()
        self.assertEqual(manager.ordering, [])

    def test_init_with_providers(self):
        providers = [
            FilesystemProvider(["/etc/foo"], "foo"),
            EnvironmentProvider("foo"),
        ]
        manager = ProviderManager(providers=providers)
        self.assertEqual(len(manager.ordering), 2)
        self.assertEqual("filesystem", manager.ordering[0])
        self.assertEqual("environment", manager.ordering[1])
        self.assertTrue(hasattr(manager, "environment"))
        self.assertTrue(hasattr(manager, "filesystem"))

    def test_get(self):
        envprovider = EnvironmentProvider("foo")
        manager = ProviderManager(providers=[envprovider])
        self.assertEqual(manager.get("environment"), envprovider)

    def test_get_none(self):
        manager = ProviderManager()
        self.assertIsNone(manager.get("filesystem"))

    def test_register_provider(self):
        manager = ProviderManager()
        manager.register(EnvironmentProvider("foo"))
        self.assertIn("environment", manager.ordering)
        self.assertTrue(hasattr(manager, "environment"))

    def test_register_duplicate_provider(self):
        manager = ProviderManager()
        manager.register(EnvironmentProvider("foo"))
        self.assertIn("environment", manager.ordering)
        self.assertTrue(hasattr(manager, "environment"))
        with self.assertLogs(level="ERROR"):
            manager.register(EnvironmentProvider("foo"))
        self.assertEqual(len(manager.ordering), 1)

    def test_deregister_provider(self):
        manager = ProviderManager()
        manager.register(EnvironmentProvider("foo"))
        self.assertIn("environment", manager.ordering)
        self.assertTrue(hasattr(manager, "environment"))
        manager.deregister("environment")
        self.assertNotIn("environment", manager.ordering)
        self.assertFalse(hasattr(manager, "environment"))

    def test_deregister_unregistered(self):
        manager = ProviderManager()
        manager.register(FilesystemProvider(["/etc/foo"], "foo"))
        manager.deregister("environment")
        self.assertIn("filesystem", manager.ordering)
        self.assertEqual(len(manager.ordering), 1)
        self.assertTrue(hasattr(manager, "filesystem"))
        self.assertNotIn("environment", manager.ordering)
        self.assertNotEqual(len(manager.ordering), 2)
